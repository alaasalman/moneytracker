import Vue from 'vue';
import TransactionFilter from './TransactionFilter.vue';

Vue.config.delimiters = ['[[', ']]'];

Vue.component('transaction-filter', TransactionFilter);

var vm = new Vue({
  el: '#transfilter',
  data: {
    ruleset: [],
  },
});
