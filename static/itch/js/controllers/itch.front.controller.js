(function() {
    'use strict';

    angular
        .module('itch.front.controllers')
        .controller('ItchController', ItchController);

    ItchController.$inject = ['$timeout', '$rootScope', '$scope', '$location', '$routeParams', 'ngDialog'];

    function ItchController($timeout, $rootScope, $scope, $location, $routeParams, ngDialog) {
        var vm = this;

// [START] Init section =============================================================================

        activate();
        function activate() {
            setWebsocketConnection();
        }

// [END] Init section ==============================================================================

// [START] Websocket section =======================================================================

        function setWebsocketConnection() {
            console.log('Opening WS connection to: ' + "ws://" + window.location.host + "/API-ws/");
            vm.ws = new WebSocket("ws://" + window.location.host + "/API-ws/");
            vm.ws.onmessage = function(e) {
                receiveWebsocketMessage(e.data);
            };
            vm.ws.onopen = function() {
                // Request information
                console.log('Opened WS connection to: ' + "ws://" + window.location.host + "/API-ws/");
                //TODO
                requestGetDetails('content', 'get_details');
            };

            // Call onopen directly if socket is already open
            if (vm.ws.readyState == WebSocket.OPEN) {vm.ws.onopen();}
        }

        function requestGetDetails(attr_a, attr_b){
            var data = {
                'attr_a': attr_a,
                'attr_b': attr_b
            };

            sendWebsocketMessage('content', 'get_details', data, -1, null)
        }


        function sendWebsocketMessage(handler, command, data, msgid, user) {
            // Construct a msg object containing the data the server needs to process the message from the chat client.
            var msg = {
                handler: handler,
                command: command,
                msgid: msgid,
                data: data
            };
            if (user != null){
                msg['user'] = user
            }
            // Send the msg object as a JSON-formatted string.
            vm.ws.send(JSON.stringify(msg));
        }

        function receiveWebsocketMessage(jsonString){
            var message = JSON.parse(jsonString);
            console.log(message);
            switch (message.command) {
                case 'details':
                    console.log(message.data);
                    break;
                default:
                    break;
            }
        }

// [END] Websocket section ========================================================================


    }

})();
