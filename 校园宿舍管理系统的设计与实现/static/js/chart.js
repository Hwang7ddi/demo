/**
 * 校园宿舍管理系统 - 数据可视化脚本
 * 
 * 提供全校学生男女比例、维修申请状态分布等数据可视化功能
 * 使用 Chart.js 实现图表绘制，支持响应式布局和动态更新
 */

// 定义 CampusCharts 命名空间
const CampusCharts = {
    /**
     * 初始化学生男女比例饼图
     * @param {string} chartId - 图表容器ID
     * @param {number} maleCount - 男生人数
     * @param {number} femaleCount - 女生人数
     * @returns {Chart} Chart.js实例
     */
    initGenderChart(chartId, maleCount, femaleCount) {
        const ctx = document.getElementById(chartId).getContext('2d');
        return new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['男生', '女生'],
                datasets: [{
                    data: [maleCount, femaleCount],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: '学生男女比例'
                    }
                }
            }
        });
    },

    /**
     * 初始化维修申请状态分布环形图
     * @param {string} chartId - 图表容器ID
     * @param {number} pending - 待处理数量
     * @param {number} processing - 处理中数量
     * @param {number} completed - 已完成数量
     * @returns {Chart} Chart.js实例
     */
    initRepairChart(chartId, pending, processing, completed) {
        const ctx = document.getElementById(chartId).getContext('2d');
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['待处理', '处理中', '已完成'],
                datasets: [{
                    data: [pending, processing, completed],
                    backgroundColor: [
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: '维修申请状态分布'
                    }
                }
            }
        });
    },

    /**
     * 启用图表响应式功能
     * @param {Array} charts - Chart.js实例数组
     */
    enableResponsive(charts) {
        window.addEventListener('resize', () => {
            charts.forEach(chart => {
                chart.resize();
            });
        });
    }
};

// 页面加载完成后初始化图表（需在页面中传入参数调用）
document.addEventListener('DOMContentLoaded', () => {
    // 示例调用（实际需在页面中根据后端数据动态调用）
    // if (typeof genderChartConfig !== 'undefined') {
    //     const genderChart = CampusCharts.initGenderChart(
    //         genderChartConfig.chartId,
    //         genderChartConfig.maleCount,
    //         genderChartConfig.femaleCount
    //     );
    // }
    // if (typeof repairChartConfig !== 'undefined') {
    //     const repairChart = CampusCharts.initRepairChart(
    //         repairChartConfig.chartId,
    //         repairChartConfig.pending,
    //         repairChartConfig.processing,
    //         repairChartConfig.completed
    //     );
    //     CampusCharts.enableResponsive([genderChart, repairChart]);
    // }
});