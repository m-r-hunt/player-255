(ns player-255.site-generator
  (:require [selmer.parser :as template]))

(defn generate-game-page
  [game]
  (if (:shortname game)
    (spit (str "docs/" (:shortname game) ".html") (template/render-file "templates/game-page.html" game))))

(defn generate
  [remaining-games played-games]
  (clojure.java.io/make-parents "docs/foo.html")
  (spit "docs/lists.html" (template/render-file "templates/lists.html" {:remaining-games remaining-games :played-games played-games}))
  (map generate-game-page played-games)
  ;; TODO Copy images to output
  nil)
