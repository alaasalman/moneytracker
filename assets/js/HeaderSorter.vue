<template>
  <div>
    <a @click.prevent="changeSortDirection">{{ sortFieldDisplay }}
      <span class="icon"><i :class="classObject"/></span>
    </a>
  </div>
</template>

<script>
  import { parse, stringify } from 'query-string';

  export default {
    props: {
      sortField: {
        type: String,
        required: true,
      },
      sortFieldDisplay: {
        type: String,
        required: true,
      },
    },
    data () {
      return {
        options: [],
        isLoading: true,
        value: this.initialValue,
        sortDirection: '',
      };
    },
    computed: {
      classObject: function () {
        let paramsObject = parse(window.location.search);

        let classObj = {
          fa: true,
        };

        if (this.sortField === paramsObject['sortby']) {
          if (this.sortDirection === 'desc') {
            classObj['fa-sort-down'] = true;
          } else if (this.sortDirection === 'asc') {
            classObj['fa-sort-up'] = true;
          } else {
            classObj['fa-sort'] = true;
          }

        } else {
          classObj['fa-sort'] = true;
        }
        return classObj;
      },
    },
    mounted: function () {
      let paramsObject = parse(window.location.search);
      if ('sortbydirection' in paramsObject) {
        this.sortDirection = paramsObject['sortbydirection'];
      }
    },
    methods: {
      changeSortDirection: function () {
        let paramsObject = parse(window.location.search);

        if (this.sortDirection === 'desc') {
          this.sortDirection = 'asc';
        } else {
          this.sortDirection = 'desc';
        }

        paramsObject['sortby'] = this.sortField;
        paramsObject['sortbydirection'] = this.sortDirection;

        location.search = stringify(paramsObject);
      },
    },
  };
</script>
