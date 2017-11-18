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
        played (conj played-games (assoc pick :rating :na))]
    (println (str "Enter rating for '" (:game (last played-games)) "':"))
    (let [rating (Integer. (read-line))]
      (println (:game pick))
      (spit "games.edn" (with-out-str (pp/pprint next-list)))
      (spit "played-games.edn" (with-out-str (pp/pprint
                                              (assoc-in played [(dec (dec (count played))) :rating] rating)))))))

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
