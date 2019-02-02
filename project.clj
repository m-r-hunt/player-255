(defproject player-255 "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.9.0"]
                 [selmer "1.12.6"]]
  :main ^:skip-aot player-255.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all}})
