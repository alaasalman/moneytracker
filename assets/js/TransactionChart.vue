<template>
  <div>
    <div class="card">
      <div
        :class="{ 'is-active': isChartTypesMenuActive }"
        class="dropdown"
      >
        <div class="dropdown-trigger">
          <button
            class="button"
            aria-haspopup="true"
            aria-controls="dropdown-menu-chart"
            @click.prevent="toggleChartTypesMenu"
          >
            <span>Chart Type</span>
            <span class="icon is-small">
              <i
                class="fas fa-angle-down"
                aria-hidden="true"
              />
            </span>
          </button>
        </div>
        <div
          id="dropdown-menu-chart"
          class="dropdown-menu"
          role="menu"
        >
          <div class="dropdown-content">
            <a
              :class="{ 'is-active': chartType === 1 }"
              class="dropdown-item"
              @click.prevent="displayChartType(1)"
            >
              Monthly
            </a>
            <a
              :class="{ 'is-active': chartType === 2 }"
              class="dropdown-item"
              @click.prevent="displayChartType(2)"
            >
              Pie by Tag
            </a>
            <a
              :class="{ 'is-active': chartType === 3 }"
              class="dropdown-item"
              @click.prevent="displayChartType(3)"
            >
              Yearly
            </a>
          </div>
        </div>
      </div>
    </div>
    <div class="small">
      <bar-chart
        v-if="chartType === 1"
        :chart-data="chartObject"
      />
      <pie-chart
        v-if="chartType === 2"
        :chart-data="chartObject"
      />
      <bar-chart
        v-if="chartType === 3"
        :chart-data="chartObject"
      />
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import { parse } from 'query-string';
  import 'chartjs-plugin-colorschemes';

  // import a particular color scheme
  //  import { Aspect6 } from 'chartjs-plugin-colorschemes/src/colorschemes/colorschemes.office';

  import BarChart from './BarChart.js';
  import PieChart from './PieChart';

  export default {
    components: {
      BarChart, PieChart,
    },
    props: {
      fromDate: {
        type: String,
        default: '',
      },
      toDate: {
        type: String,
        default: '',
      },
      monthlyUrl: {
        type: String,
        required: true,
      },
      pieUrl: {
        type: String,
        required: true,
      },
      yearlyUrl: {
        type: String,
        required: true,
      },
    },
    data () {
      return {
        chartObject: null,
        isChartTypesMenuActive: false,
        chartType: 1, // 1 is for monthly, 2 for pie by tag, 3 is yearly
      };
    },
    computed: {
      chartUrl: function () {
        if (this.chartType === 1) {
          return this.monthlyUrl;
        } else if (this.chartType === 2) {
          return this.pieUrl;
        } else if (this.chartType === 3) {
          return this.yearlyUrl;
        }
      },
    },
    watch: {
      chartType: function (oldValChartType, newValChartType) {
        this.updateChartData();
        this.toggleChartTypesMenu();
      },
    },
    mounted () {
      this.updateChartData();
    },
    methods: {
      toggleChartTypesMenu: function () {
        this.isChartTypesMenuActive = !this.isChartTypesMenuActive;
      },
      displayChartType: function (chartId) {
        this.chartType = chartId;
      },
      updateChartData: function () {
        let paramsObject = parse(window.location.search);
        paramsObject['date__gte'] = this.fromDate;
        paramsObject['date__lte'] = this.toDate;

        axios.get(this.chartUrl, {
          params: paramsObject,
        }).then((response) => {

          this.chartObject = {
            labels: response.data.labels,
            datasets: [
              {
                label: response.data.label,
                //backgroundColor: '#f87979',
                data: response.data.data,
              },
            ],
            options: {
              plugins: {
                colorschemes: {
                  scheme: 'brewer.Paired12',
                },
              },
            },
          };

        }).catch(function (error) {
          console.log(error);
        });
      },
    },
  };
</script>

<style>
  .small {
    max-width: 600px;
    margin: 20px auto;
  }
</style>
