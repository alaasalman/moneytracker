import Vue from 'vue';
import Datepicker from 'vue-bulma-datepicker';
import VueCsvImport from 'vue-csv-import';
import TagMultiSelect from './TagMultiSelect';
import HeaderSorter from './HeaderSorter';

Vue.component('tag-multi-select', {
  extends: TagMultiSelect,
});

Vue.component('header-sorter', {
  extends: HeaderSorter,
});

new Vue({
  el: '.cdate',
  components: {
    Datepicker: Datepicker,
  },
});

new Vue({
  el: '.tagmultiselect',
});

new Vue({
  el: '.vue-header-sorter1',
});

new Vue({
  el: '.vue-header-sorter2',
});

new Vue({
  el: '#vue_csv_import',
  components: { VueCsvImport },
});
