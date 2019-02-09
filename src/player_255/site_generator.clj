(ns player-255.site-generator
  (:require [selmer.parser :as template]
            [selmer.filters :as filters]))

(filters/add-filter! :status (fn [s] (clojure.string/capitalize (name s))))

(filters/add-filter! :remove-title-credits
                     (fn [s]
                       (filterv #(not (or (= (clojure.string/upper-case (last (clojure.string/split % #"-"))) "TITLE.PNG")
                                          (= (clojure.string/upper-case (last (clojure.string/split % #"-"))) "CREDITS.PNG")))
                                s)))

(filters/add-filter! :has-credits?
                     (fn [s]
                       (some? (seq (filter #(= (clojure.string/upper-case (last (clojure.string/split % #"-"))) "CREDITS.PNG") s)))))

(defn generate-game-page
  [game]
  (if (:shortname game)
    (spit (str "docs/" (:shortname game) ".html") (template/render-file "templates/game-page.html" game))))

(defn get-screenshots
  [played-games]
  (let [fs (file-seq (clojure.java.io/file "static-assets/images/screenshots"))]
    (into [] (reduce (fn [played-games file]
                       (let [filename (.getName file)
                             shortname (first (clojure.string/split filename #"-"))
                             part (second (clojure.string/split filename #"-"))]
                         (map #(if (= (:shortname %) shortname)
                                 (update % :screenshots conj filename)
                                 %)
                              played-games)))
                     (map #(assoc % :screenshots []) played-games)
                     fs))))

(defn make-links
  [played-games]
  (map #(assoc %1 :next (:shortname %2) :prev (:shortname %3))
       played-games
       (drop 1 (conj played-games {}))
       (conj (butlast played-games) {})))

(defn generate
  [remaining-games played-games]
  (let [played-games (make-links (get-screenshots played-games))]
    (clojure.java.io/make-parents "docs/foo.html")
    (spit "docs/lists.html" (template/render-file "templates/lists.html" {:remaining-games remaining-games :played-games played-games}))
    (dorun (map generate-game-page played-games))
    (spit "docs/index.html" (template/render-file "templates/index.html" {:recent-games (take 10 (drop 1 (reverse played-games)))
                                                                          :next-up (last played-games)
                                                                          :count (dec (count played-games))
                                                                          :percent (float (* (/ (dec (count played-games)) 255) 100))}))
    ;; TODO Copy images to output
    nil))
