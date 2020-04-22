import 'bulma/css/bulma.css';
import Vue from 'vue';
import * as Sentry from '@sentry/browser';
import * as Integrations from '@sentry/integrations';
import { dom, library } from '@fortawesome/fontawesome-svg-core';
import {
  faHome, faBook, faMoneyBillAlt,
  faChartArea, faRedo, faTags,
  faTrash, faEdit, faUpload,
  faInfo, faEnvelope, faCheck,
  faMinusCircle, faPlusSquare, faSort,
  faSortDown, faSortUp, faAngleDown,
  faList, faBlog
} from '@fortawesome/free-solid-svg-icons';

Vue.config.delimiters = ['[[', ']]'];

library.add(
  faHome, faBook, faMoneyBillAlt,
  faChartArea, faRedo, faTags,
  faTrash, faEdit, faUpload,
  faInfo, faEnvelope, faCheck,
  faMinusCircle, faPlusSquare, faSort,
  faSortDown, faSortUp, faAngleDown,
  faList, faBlog
);
// will automatically find any <i> tags in the page and replace those with <svg> elements
dom.watch(); // This will kick of the initial replacement of i to svg tags and configure a MutationObserver

Sentry.init({
  dsn: 'https://f5ea7a819860428ba6dddbe5c1e47044@o123413.ingest.sentry.io/5199529',
  integrations: [new Integrations.Vue({Vue, attachProps: true, logErrors: true})],
});


