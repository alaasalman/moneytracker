import 'bulma/css/bulma.css';
import Vue from 'vue';
import { dom, library } from '@fortawesome/fontawesome-svg-core';
import {
  faHome, faBook, faMoneyBillAlt,
  faChartArea, faRedo, faTags,
  faTrash, faEdit, faUpload,
  faInfo, faEnvelope, faCheck,
  faMinusCircle, faPlusSquare, faSort,
  faSortDown, faSortUp, faAngleDown,
  faList,
} from '@fortawesome/free-solid-svg-icons';

Vue.config.delimiters = ['[[', ']]'];

library.add(
  faHome, faBook, faMoneyBillAlt,
  faChartArea, faRedo, faTags,
  faTrash, faEdit, faUpload,
  faInfo, faEnvelope, faCheck,
  faMinusCircle, faPlusSquare, faSort,
  faSortDown, faSortUp, faAngleDown,
  faList,
);
// will automatically find any <i> tags in the page and replace those with <svg> elements
dom.watch(); // This will kick of the initial replacement of i to svg tags and configure a MutationObserver



