(function() {
    'use strict';

    angular
        .module('itch.routes')
        .config(config);

    config.$inject = ['$routeProvider'];

    function config($routeProvider) {
        $routeProvider.when('/', {
            controller: 'ItchController',
            controllerAs: 'vm',
            templateUrl: '/static/itch/templates/itch_app.html'
        }).otherwise({
            redirectTo: '/'
        });
    }
})();
