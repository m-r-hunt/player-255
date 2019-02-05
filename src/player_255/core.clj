(ns player-255.core
  (:gen-class)
  (:require [clojure.edn :as edn]
            [clojure.pprint :as pp]
            [player-255.site-generator :as site-generator]))

(def games (edn/read-string (slurp "games.edn")))
(def played-games (edn/read-string (slurp "played-games.edn")))

(defn datestamp
  []
  (let [calendar (java.util.Calendar/getInstance)]
    (str (.get calendar java.util.Calendar/YEAR)
         "-"
         (inc (.get calendar java.util.Calendar/MONTH))
         "-"
         (.get calendar java.util.Calendar/DAY_OF_MONTH))))

(defn get-filenames
  [dry-run]
  (if dry-run
    ["games.test.edn"
     "played-games.test.edn"]
    ["games.edn"
     "played-games.edn"]))

(defn ask
  [prompt]
  (println prompt)
  (read-line))

(defn ask-status
  [game]
  (println (str "Status of " game " ? (c)omplete (n)ot complete (o)ther"))
  (case (first (read-line))
    \c [:status :complete]
    \n [:status :not-complete]
    [:status :other :status-note (ask "Enter status note:")]))

(defn gather-input
  [game]
  (-> []
      (conj :rating (Integer. (ask (str "Enter rating for '" game "':"))))
      (conj :completion-date (datestamp))
      (conj :shortname (ask "Enter shortname:"))
      (conj :notes (ask "Enter notes:"))
      (concat (ask-status game))))

(defn old-main
  "Get input about the last played game, pick the next one, and regenerate the site."
  [& args]
  (let [dry-run (some #(= "--dry-run" %) *command-line-args*)
        pick (rand-nth games)
        next-list (into [] (remove #(= % pick) games))
        played (conj played-games (assoc pick :rating :na))
        [games-file played-games-file] (get-filenames dry-run)
        input (gather-input (:game (last played-games)))
        n (dec (dec (count played)))
        next-played (update played n #(apply assoc % input))]
    (println (str "Next up: " (:game pick)))
    (spit games-file (with-out-str (pp/pprint next-list)))
    (spit played-games-file (with-out-str (pp/pprint next-played)))
    (site-generator/generate next-list next-played)))

(defn stats
  []
  (reduce #(case (:rating %2)
             1 (update-in (update-in %1 [:ones] inc) [:worst] conj (:game %2))
             2 (update-in %1 [:twos] inc)
             3 (update-in %1 [:threes] inc)
             4 (update-in %1 [:fours] inc)
             5 (update-in (update-in %1 [:fives] inc) [:best] conj (:game %2))
               %1)
          {:ones 0 :twos 0 :threes 0 :fours 0 :fives 0 :best [] :worst []}
          played-games))

(defn csv
  []
  (let [csv-data (apply str (map #(str (:game %) "," (:rating %) "," (:meta-rating %) "\n")
                                 (butlast played-games)))]
    (spit "played-games.csv" csv-data)))

(defn data-entry-shortname
  [game]
  (if (not (:shortname game))
    (assoc game :shortname (ask (str "Enter shortname for " (:game game) ":")))
    game))

(defn data-entry-status
  [game]
  (if (not (:status game))
    (apply assoc game (ask-status (:game game)))
    game))

(defn data-entry-notes
  [game]
  (if (not (:notes game))
    (do
      (println (str "Enter notes for " (:game game) ":"))
      (loop [game game]
        (let [input (read-line)]
          (if (= input "dexit")
            game
            (recur (update game :notes str input "\n"))))))
    game))

(defn data-entry-date
  [game]
  (if (not (:completion-date game))
    (assoc game :completion-date (ask (str "Enter completion date for " (:game game) ":")))
    game))

(defn data-entry
  [game]
  (-> game
      (data-entry-shortname)
      (data-entry-date)
      (data-entry-status)
      (data-entry-notes)))

(defn -main
  []
  (loop [i 0 played-games (edn/read-string (slurp "played-games.edn"))]
    (if (< i (count played-games))
      (if (or (not (:shortname (nth played-games i)))
              (not (:status (nth played-games i)))
              (not (:notes (nth played-games i)))
              (not (:completion-date (nth played-games i))))
        (let [played-games (update played-games i data-entry)]
          (spit "played-games.edn" (with-out-str (pp/pprint played-games)))
          (recur (inc i) played-games))
        (recur (inc i) played-games)))))
