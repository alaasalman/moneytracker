<template>
  <div>
    <multiselect
      v-model="value"
      :multiple="true"
      :hide-selected="true"
      :clear-on-select="true"
      :value="initialValue"
      :max="3"
      :loading="isLoading"
      :options="options"
      placeholder="Select tag"
      track-by="slug"
      label="name"
    />

    <input
      :name="identifier"
      :value="selectedOptions"
      type="hidden"
    >
  </div>
</template>

<script>
  import Multiselect from 'vue-multiselect';
  import axios from 'axios';

  export default {
    components: { Multiselect },
    props: {
      url: {
        type: String,
        required: true,
      },
      identifier: {
        type: String,
        required: true,
      },
      initialValue: {
        type: Array,
        default: function () {
          return [];
        },
        required: false,
      },
    },
    data () {
      return {
        options: [],
        isLoading: true,
        value: this.initialValue,
      };
    },
    computed: {
      selectedOptions: function () {
        return this.value.map(sel => sel.name).join();
      },
    },
    mounted: function () {
      axios.get(this.url).then((response) => {

        for (let t of response.data) {
          this.options.push(t);
        }
      }).catch(function (error) {
        console.log(error);
      }).finally(() => {
        this.isLoading = false;
      });
    },
  };
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
