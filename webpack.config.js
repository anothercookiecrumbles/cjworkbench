var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require('extract-text-webpack-plugin')

module.exports = {
  context: __dirname,

  // Each page gets its own bundle
  entry: {
    app: './assets/js/app',
    workflows: './assets/js/workflows',
    workflow: './assets/js/workflow'
  },

  output: {
    path: path.resolve('./assets/bundles/'),
    filename: "[name]-[hash].js",
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new ExtractTextPlugin({ filename: 'assets/main.css', allChunks: true })
  ],

  module: {
    rules: [
      {
        test: /\.jsx?$/,
        // chartbuilder and included modules need their jsx compiled, but most node-modules do not
        exclude: /node_modules(?!\/(react-tangle))/,
        loader: 'babel-loader',
        query: {presets: ['es2015', 'react']}  // to transform JSX into JS
      },
      {
        test: /\.css$/, // required to load e.g. React Data-Grid css. Results in lots of duplicated css
        loaders: ['style-loader', 'css-loader']
      },
      {
        test: /\.scss$/,
        loaders: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: ['css-loader', 'sass-loader']
        })
      }
    ]
  },

  resolve: {
    modules: ['node_modules', 'chartbuilder'],
    extensions: ['.js', '.jsx']
  },
}
