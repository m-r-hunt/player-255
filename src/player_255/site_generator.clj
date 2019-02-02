(ns player-255.site-generator
  (:require [selmer.parser :as template]))

(defn generate
  [remaining-games played-games]
  (template/render-file "templates/lists.html" {:remaining-games remaining-games}))
