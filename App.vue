<script>
export default {
  globalData: {
    userInfo: null,
    token: '',
    baseUrl: 'http://localhost:8080/api',
    userRole: '',
    setUserInfo: null,
    clearUserInfo: null,
    updateTabBar: null
  },

  onLaunch: function () {
    const token = uni.getStorageSync('token')
    const userInfo = uni.getStorageSync('userInfo')
    const userRole = uni.getStorageSync('userRole')
    
    // 将方法挂载到 globalData
    this.globalData.setUserInfo = this.setUserInfo.bind(this)
    this.globalData.clearUserInfo = this.clearUserInfo.bind(this)
    this.globalData.updateTabBar = this.updateTabBar.bind(this)
    
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = JSON.parse(userInfo)
      this.globalData.userRole = userRole
      // 根据角色更新tabBar
      setTimeout(() => {
        this.updateTabBar(userRole)
      }, 100)
      // 根据角色跳转到对应端首页
      if (userRole === 'admin') {
        setTimeout(() => {
          uni.reLaunch({
            url: '/pages/admin/index/index'
          })
        }, 200)
      } else if (userRole === 'grid') {
        setTimeout(() => {
          uni.reLaunch({
            url: '/pages/grid/index/index'
          })
        }, 200)
      }
    }
  },

  onShow: function () {
    console.log('App Show')
  },

  onHide: function () {
    console.log('App Hide')
  },

  // 更新tabBar配置
  updateTabBar: function (role) {
    if (role === 'grid' || role === 'admin') {
      // 网格员端tabBar配置
      const gridTabList = [
        {
          pagePath: 'pages/grid/index/index',
          text: '首页',
          iconPath: 'static/images/home.png',
          selectedIconPath: 'static/images/home-active.png'
        },
        {
          pagePath: 'pages/grid/tasks/tasks',
          text: '任务',
          iconPath: 'static/images/task.png',
          selectedIconPath: 'static/images/task-active.png'
        },
        {
          pagePath: 'pages/grid/alerts/alerts',
          text: '预警',
          iconPath: 'static/images/alert.png',
          selectedIconPath: 'static/images/alert-active.png'
        },
        {
          pagePath: 'pages/grid/profile/profile',
          text: '我的',
          iconPath: 'static/images/profile.png',
          selectedIconPath: 'static/images/profile-active.png'
        }
      ]
      
      // 动态更新tabBar
      uni.setTabBarStyle({
        selectedColor: '#43a047',
        borderStyle: 'black'
      })
      
      // 逐个更新tabBar项
      gridTabList.forEach((item, index) => {
        uni.setTabBarItem({
          index: index,
          pagePath: item.pagePath,
          text: item.text,
          iconPath: item.iconPath,
          selectedIconPath: item.selectedIconPath
        })
      })
    } else {
      // 村民端tabBar配置
      const villagerTabList = [
        {
          pagePath: 'pages/villager/index/index',
          text: '首页',
          iconPath: 'static/images/home.png',
          selectedIconPath: 'static/images/home-active.png'
        },
        {
          pagePath: 'pages/villager/alerts/alerts',
          text: '预警',
          iconPath: 'static/images/alert.png',
          selectedIconPath: 'static/images/alert-active.png'
        },
        {
          pagePath: 'pages/villager/guides/guides',
          text: '指南',
          iconPath: 'static/images/task.png',
          selectedIconPath: 'static/images/task-active.png'
        },
        {
          pagePath: 'pages/villager/profile/profile',
          text: '我的',
          iconPath: 'static/images/profile.png',
          selectedIconPath: 'static/images/profile-active.png'
        }
      ]
      
      // 重置tabBar样式
      uni.setTabBarStyle({
        selectedColor: '#1e88e5',
        borderStyle: 'black'
      })
      
      // 逐个更新tabBar项
      villagerTabList.forEach((item, index) => {
        uni.setTabBarItem({
          index: index,
          pagePath: item.pagePath,
          text: item.text,
          iconPath: item.iconPath,
          selectedIconPath: item.selectedIconPath
        })
      })
    }
  },

  setUserInfo: function (userInfo, token, role) {
    this.globalData.userInfo = userInfo
    this.globalData.token = token
    this.globalData.userRole = role
    uni.setStorageSync('token', token)
    uni.setStorageSync('userInfo', JSON.stringify(userInfo))
    uni.setStorageSync('userRole', role)
    // 更新tabBar
    setTimeout(() => {
      this.updateTabBar(role)
    }, 100)
  },

  clearUserInfo: function () {
    this.globalData.userInfo = null
    this.globalData.token = ''
    this.globalData.userRole = ''
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
    uni.removeStorageSync('userRole')
    // 重置为村民端tabBar
    setTimeout(() => {
      this.updateTabBar('villager')
    }, 100)
  },

  request: function (options) {
    const { url, method = 'GET', data = {}, header = {} } = options
    
    const token = this.globalData.token
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    return new Promise((resolve, reject) => {
      uni.request({
        url: this.globalData.baseUrl + url,
        method: method,
        data: data,
        header: {
          'content-type': 'application/json',
          ...header
        },
        success: (res) => {
          if (res.statusCode === 200) {
            if (res.data.code === 200) {
              resolve(res.data.data)
            } else {
              uni.showToast({
                title: res.data.message,
                icon: 'none'
              })
              reject(res.data)
            }
          } else {
            uni.showToast({
              title: '请求失败',
              icon: 'none'
            })
            reject(res)
          }
        },
        fail: (err) => {
          uni.showToast({
            title: '网络错误',
            icon: 'none'
          })
          reject(err)
        }
      })
    })
  }
}
</script>

<style>
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.container {
  padding: 20rpx;
}

.btn {
  background: linear-gradient(135deg, #1e88e5, #1976d2);
  color: #fff;
  border-radius: 16rpx;
  padding: 32rpx;
  text-align: center;
  font-size: 32rpx;
  font-weight: 500;
  margin-top: 40rpx;
}

.btn:active {
  opacity: 0.8;
}

.form {
  padding: 40rpx 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  background: #fff;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 30rpx;
  border: 2rpx solid #eee;
}

.form-input:focus {
  border-color: #1e88e5;
}

.card {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
}

.card-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}

.status-danger {
  color: #f44336;
  background: #ffebee;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
}

.status-warning {
  color: #ff9800;
  background: #fff3e0;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
}

.status-success {
  color: #4caf50;
  background: #e8f5e9;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
}
</style>
