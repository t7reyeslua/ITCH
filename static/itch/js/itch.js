(function() {
    'use strict';

    angular
        .module('itch', [
            'ngTouch',
            'angular-kaarousel',
            'itch.config',
            'itch.routes',
            'itch.front'
        ]);

    angular
        .module('itch.config', []);

    angular
        .module('itch.routes', ['ngRoute']);

    angular
        .module('itch')
        .run(run);

    run.$inject = ['$http'];
    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }

})();
