(function() {
    'use strict';

    angular
        .module('itch.front', ['itch.front.controllers', 'ngSanitize', 'ngDialog']);

    angular
        .module('itch.front.controllers', ['ngSanitize']);
})();
