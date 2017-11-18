(ns player-255.core
  (:gen-class)
  (:require [clojure.edn :as edn]
            [clojure.pprint :as pp]))

(def games (edn/read-string (slurp "games.edn")))
(def played-games (edn/read-string (slurp "played-games.edn")))

(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (let [pick (rand-nth games)
        next-list (into [] (remove #(= % pick) games))
        played (conj played-games {:game pick :rating :na})]
    (println "Enter rating for " + (:game (last played)))
    (let [rating (read-line)]
      (println pick)
      (spit "games.edn" (with-out-str (pp/pprint next-list)))
      (spit "played-games.edn" (with-out-str (pp/pprint
                                              (assoc-in played [(length player) :rating] rating)))))))
