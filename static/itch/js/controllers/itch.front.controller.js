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

        $scope.chat_array = [];
        $scope.side = 'right';
        $scope.map_image = '/static/common/images/map_ams.png';

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

        function updateScroll(){
            var element = document.getElementById("chatbox");
            element.scrollTop = element.scrollHeight;
        }

        function receiveWebsocketMessage(jsonString){
            var message = JSON.parse(jsonString);
            console.log(message);

            if ("undefined" !== typeof message.data.message ) {
                var data_msg = {
                    'message': message.data.message,
                    'side': $scope.side
                };

                if (message.data.message == "Welcome to Amsterdam. What can I do for you?" ||
                    message.data.message == "OK." || message.data.message == "No problem.") {
                    console.info('same string');
                    $scope.chat_array = [];
                } else {
                    $scope.chat_array.push(data_msg);
                }

                if (message.data.hasOwnProperty('image')) {
                    $scope.map_image = message.data.image;
                }
                $timeout(function () {
                    updateScroll();
                }, 100);
                $timeout(function(){
                    $scope.$digest();
                });
            }

            console.info($scope.chat_array);
            if ($scope.side === 'right'){
                $scope.side = 'left';
            } else {
                // $scope.side = 'right';
                $scope.side = 'left';
            }
            $timeout(function(){
                $scope.$digest();
            });

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
