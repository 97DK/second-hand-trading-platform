const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  css: {
    loaderOptions: {
      scss: {
        additionalData: `
          @forward "element-plus/theme-chalk/src/common/var.scss" with (
            $colors: (
              "primary": (
                "base": #737BBE,
              ),
            ),
          );
        `
      }
    }
  }
})