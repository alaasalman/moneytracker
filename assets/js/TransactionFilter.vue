<template>
  <div id="transactionfilter">
    <div class="card">
      <form
        id="filterform"
        @submit.prevent="onSubmit"
      >
        <header class="card-header">
          <p class="card-header-title">
            Filter
          </p>
        </header>
        <div class="card-content">
          <div class="field is-horizontal is-grouped">
            <div class="field-label is-normal">
              <label class="label">Between</label>
            </div>
            <div class="field-body">
              <div class="columns is-vcentered">
                <div class="column">
                  <div class="control">
                    <datepicker
                      id="from_date"
                      :config="{ dateFormat: 'Y-m-d', static: true }"
                      :value="fromDate"
                      name="date__gte"
                      placeholder="From"
                    />
                  </div>
                </div>
                <div class="column">
                  <div class="control">
                    <datepicker
                      id="to_date"
                      :config="{ dateFormat: 'Y-m-d', static: true }"
                      :value="toDate"
                      name="date__lte"
                      placeholder="To"
                    />
                  </div>
                </div>
                <div class="column">
                  <div
                    :class="{ 'is-active': isFiltersActive }"
                    class="dropdown"
                  >
                    <div class="dropdown-trigger">
                      <button
                        class="button is-link is-rounded"
                        aria-haspopup="true"
                        aria-controls="dropdown-menu2"
                        @click.prevent="toggleFilters"
                      >
                        <span>Add Rule</span>
                        <span class="icon is-small">
                          <i
                            class="fas fa-angle-down"
                            aria-hidden="true"
                          />
                        </span>
                      </button>
                    </div>
                    <div
                      id="dropdown-menu2"
                      class="dropdown-menu"
                      role="menu"
                    >
                      <div class="dropdown-content">
                        <a
                          class="dropdown-item"
                          @click.prevent="activateFilter(1)"
                        >
                          Amount &le;
                          <span
                            v-if="hasAmountFilter"
                            class="icon is-small"
                          >
                            <i class="fas fa-check"/>
                          </span>
                        </a>
                        <a
                          class="dropdown-item"
                          @click.prevent="activateFilter(2)"
                        >
                          Description Contains
                          <span
                            v-if="hasDescriptionFilter"
                            class="icon is-small"
                          >
                            <i class="fas fa-check"/>
                          </span>
                        </a>
                        <a
                          class="dropdown-item"
                          @click.prevent="activateFilter(3)"
                        >
                          Description doesn't Contain
                          <span
                            v-if="hasNotDescriptionFilter"
                            class="icon is-small"
                          >
                            <i class="fas fa-check"/>
                          </span>
                        </a>
                        <a
                          class="dropdown-item"
                          @click.prevent="activateFilter(4)"
                        >
                          Tags Have
                          <span
                            v-if="hasTagsFilter"
                            class="icon is-small"
                          >
                            <i class="fas fa-check"/>
                          </span>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- dynamic rules -->
          <div
            v-if="hasAmountFilter"
            class="field is-horizontal is-narrow"
          >
            <div class="field-label is-normal">
              <label class="label">Amount &le;</label>
            </div>
            <div class="field-body">
              <div class="columns">
                <div class="column is-6">
                  <input
                    :value="amount"
                    type="number"
                    name="amount__lte"
                    class="input"
                  >
                </div>
                <div class="column is-offset-5">
                  <a
                    class="button"
                    @click.prevent="deactivateFilter(1)"
                  >
                <span class="icon is-small">
                  <i class="fas fa-minus-circle"/>
                </span>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="hasDescriptionFilter"
            class="field is-horizontal is-narrow"
          >
            <div class="field-label is-normal">
              <label class="label">Description Contains</label>
            </div>
            <div class="field-body">
              <div class="columns">
                <div class="column is-11">
                  <input
                    :value="hasDescription"
                    type="text"
                    name="description__has"
                    class="input"
                  >
                </div>
                <div class="column">
                  <a
                    class="button"
                    @click.prevent="deactivateFilter(2)"
                  >
                <span class="icon is-small">
                  <i class="fas fa-minus-circle"/>
                </span>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="hasNotDescriptionFilter"
            class="field is-horizontal is-narrow"
          >
            <div class="field-label is-normal">
              <label class="label">Description doesn't Contain</label>
            </div>
            <div class="field-body">
              <div class="columns">
                <div class="column is-11">
                  <input
                    :value="hasNotDescription"
                    type="text"
                    name="description__hasnot"
                    class="input"
                  >
                </div>
                <div class="column">
                  <a
                    class="button"
                    @click.prevent="deactivateFilter(3)">
                <span class="icon is-small">
                  <i class="fas fa-minus-circle"/>
                </span>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="hasTagsFilter"
            class="field is-horizontal is-narrow">
            <div class="field-label is-normal">
              <label class="label">Tags Include</label>
            </div>
            <div class="field-body">
              <div class="columns">
                <div class="column is-11">
                  <tag-multi-select
                    :url="accountTagsUrl"
                    :initial-value="hasTags"
                    identifier="tags__have"
                  />
                </div>
                <div class="column is-1">
                  <a
                    class="button"
                    @click.prevent="deactivateFilter(4)">
              <span class="icon is-small">
                <i class="fas fa-minus-circle"/>
              </span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <footer class="card-footer">
          <input
            type="submit"
            value="Filter"
            class="button is-link"
          >
        </footer>
      </form>
    </div>
  </div>
</template>

<script>
  import Datepicker from 'vue-bulma-datepicker';
  import {parse} from 'query-string';
  import TagMultiSelect from './TagMultiSelect';

  export default {
    components: {
      Datepicker, TagMultiSelect,
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
      accountTagsUrl: {
        type: String,
        required: true,
      },
      tagsValue: {
        type: Array,
        required: false,
        default: function () {
          return [];
        },
      },
    },
    data() {
      return {
        isFiltersActive: false,
        hasAmountFilter: false,
        hasDescriptionFilter: false,
        hasNotDescriptionFilter: false,
        hasTagsFilter: false,
        amount: 0,
        hasDescription: '',
        hasNotDescription: '',
        hasTags: [],
      };
    },
    mounted: function () {
      let paramsObject = parse(window.location.search);

      if ('amount__lte' in paramsObject) {
        this.hasAmountFilter = true;
        this.amount = paramsObject['amount__lte'];
      }

      if ('description__has' in paramsObject) {
        this.hasDescriptionFilter = true;
        this.hasDescription = paramsObject['description__has'];
      }

      if ('description__hasnot' in paramsObject) {
        this.hasNotDescriptionFilter = true;
        this.hasNotDescription = paramsObject['description__hasnot'];
      }

      if ('tags__have' in paramsObject) {
        this.hasTagsFilter = true;
        this.hasTags = this.tagsValue;
      }
    },
    methods: {
      activateFilter: function (filterID) {
        switch (filterID) {
          case 1:
            this.hasAmountFilter = true;
            break;
          case 2:
            this.hasDescriptionFilter = true;
            break;
          case 3:
            this.hasNotDescriptionFilter = true;
            break;
          case 4:
            this.hasTagsFilter = true;
            break;
        }
        this.toggleFilters();
      },
      deactivateFilter: function (filterID) {
        switch (filterID) {
          case 1:
            this.hasAmountFilter = false;
            break;
          case 2:
            this.hasDescriptionFilter = false;
            break;
          case 3:
            this.hasNotDescriptionFilter = false;
            break;
          case 4:
            this.hasTagsFilter = false;
            break;
        }
      },
      toggleFilters: function () {
        this.isFiltersActive = !this.isFiltersActive;
      },
      onSubmit: function (event) {
        event.target.submit();
      },
    },
  };
</script>

<style lang="scss">
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
  }
</style>
