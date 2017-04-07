(function() {

    'use strict';

    KaarouselController.$inject = ["$scope", "$element", "$attrs", "$interval", "$window", "$timeout", "$swipe"];
    angular
        .module('angular-kaarousel', ['ngTouch'])
        .directive('kaarousel', kaarousel);

    /** @ngInject */
    function kaarousel() {
        var directive = {
            restrict: 'EA',
            scope: {
                displayed: '=?',
                perSlide: '=?',
                autoplay: '=?',
                direction: '=?',
                pauseOnHover: '=?',
                centerActive: '=?',
                timeInterval: '=?',
                transitionDuration: '=?',
                updateRate: '=?',
                stopAfterAction: '=?',
                hideNav: '=?',
                hidePager: '=?',
                navOnHover: '=?',
                pagerOnHover: '=?',
                swipable: '=?',
                sync: '=?',
                data: '=?',
                animation: '=?',
                loop: '=?',
                options: '=?',
                afterSlide: '&?',
                beforeSlide: '&?',
                minWidth: '=?',
                expand: '=?',
                alwaysFill: '=?',
                moveNext: '=?',
                movePrev: '=?',
                currentIndex: '=?',
                currentPage: '=?'
            },
            templateUrl: '/static/common/components/angular-kaarousel/angular-kaarousel.html',
            transclude: true,
            controller: KaarouselController,
            controllerAs: 'kc'
        };

        return directive;
    }

    /** @ngInject */
    function KaarouselController($scope, $element, $attrs, $interval, $window, $timeout, $swipe) {

        // @todo some settings don't work ( mainly when center active )
        var vm = this;

        var PREFIX = 'kaarousel';

        var booleanAttributes = [
            'autoplay',
            'pauseOnHover',
            'centerActive',
            'stopAfterAction',
            'hideNav',
            'hidePager',
            'navOnHover',
            'pagerOnHover',
            'swipable',
            'loop',
            'expand',
            'alwaysFill'
        ];

        var animations = [
            'slide',
            'fade'
        ];

        var kOptions = [
            'displayed',
            'perSlide',
            'autoplay',
            'direction',
            'pauseOnHover',
            'centerActive',
            'timeInterval',
            'transitionDuration',
            'updateRate',
            'stopAfterAction',
            'hideNav',
            'hidePager',
            'navOnHover',
            'pagerOnHover',
            'swipable',
            'sync',
            'animation',
            'loop',
            'options',
            'afterSlide',
            'beforeSlide',
            'minWidth',
            'expand',
            'alwaysFill',
            'moveNext',
            'movePrev',
            'currentIndex',
            'currentPage'
        ];

        vm.init = init;
        vm.register = register;
        vm.removeSlide = removeSlide;
        vm.move = move;
        vm.play = play;
        vm.stop = stop;
        vm.movePage = movePage;
        vm.getPages = getPages;

        vm.defaultOptions = {
            displayed: 3,
            perSlide: 1,
            autoplay: true,
            direction: 'horizontal',
            pauseOnHover: true,
            centerActive: false,
            timeInterval: 3000,
            transitionDuration: 500,
            stopAfterAction: false,
            hideNav: false,
            hidePager: false,
            navOnHover: false,
            pagerOnHover: false,
            swipable: true,
            sync: null,
            animation: 'slide',
            loop: true,
            afterSlide: null,
            beforeSlide: null,
            minWidth: null,
            expand: true,
            swipeThreshold: 100,
            alwaysFill: true,
            moveNext: 0,
            movePrev: 0,
            currentIndex: 0,
            currentPage: 0
        };

        vm.state = {};

        /////////////////////////

        setElements();

        function init() {
            setOptions();
            setWatchers();

            vm.ready = true;
        }

        function getPages() {
            if (!vm.slides) return;
            return new Array(Math.ceil(vm.slides.length / vm.options.perSlide));
        }

        function setElements() {
            vm.kaarousel = $element[0];
            vm.kaarousel.classList.add(PREFIX);

            //////////////////////

            vm.kaarouselSliderContainer = vm.kaarousel.querySelector(PREFIX + '-slider-container');
            vm.kaarouselWrapper = vm.kaarousel.querySelector(PREFIX + '-wrapper');
            vm.kaarouselSlider = vm.kaarousel.querySelector(PREFIX + '-slider');
        }

        function getScopeOptions() {
            var options = {};
            if (!_.isEmpty($scope.options)) {
                options = angular.copy($scope.options);

                // Add callbacks
                options.afterSlide = $scope.afterSlide;
                options.beforeSlide = $scope.beforeSlide;

                return options;
            }
            _.forEach(kOptions, function(option) {
                options[option] = angular.isDefined($scope[option]) ? $scope[option] : vm.defaultOptions[option];
            });

            options = assumeBoolean(options);

            return options;
        }

        /**
         * Assume that an empty attr means a true value
         * @param  {Object} options Options to check
         * @return {Object}         return back the options
         */
        function assumeBoolean(options) {
            _.forEach(options, function(option, optionName) {
                if (booleanAttributes.indexOf(optionName) !== -1 && $attrs.hasOwnProperty(optionName) && angular.isUndefined(option)) {
                    options[optionName] = true;
                }
            });

            return options;
        }

        function setAnimationClass(value) {
            _.forEach(animations, function(name) {
                vm.kaarouselSlider.classList.remove(name + '-animation');
            });

            vm.kaarouselSlider.classList.add(value + '-animation');

            _.forEach(vm.slides, function(slide) {
                slide.element.css({
                    'transition-duration': value === 'slide' ? '' : vm.options.transitionDuration / 1000 + 's'
                });
            });
        }

        /**
         * Custom actions to do when particular settings are changing
         * @param  {String} option the setting
         * @param  {String} value  the setting's value
         */
        function handleImportantChanges(option, value) {
            var fn;

            switch (option) {
                case 'timeInterval':
                    stop();
                    play();
                    break;
                case 'animation':
                    setAnimationClass(value);
                    break;
                case 'direction':
                    setSliderDirection();
                    break;
                case 'autoplay':
                    fn = value ? 'play' : 'stop';
                    vm[fn]();
                    break;
                case 'swipable':
                    swipeHandler(value);
                    break;
                case 'loop':
                    if (value && !vm.isPlaying && vm.options.autoplay) play();
                    break;
                case 'transitionDuration':
                    setTransition();
                    break;
                case 'sync':
                    handleSync(value);
                    break;
                case 'centerActive':
                    move(vm.currentIndex, false, true);
                    break;
                case 'perSlide':
                    move(vm.currentIndex, false, true);
                    break;
                case 'minWidth':
                    setSlidesDimensions();
                    break;
                case 'alwaysFill':
                    vm.move(vm.currentIndex, false, true);
                    break;
                case 'moveNext':
                    vm.move(true, true);
                    break;
                case 'movePrev':
                    vm.move(null, true);
                    break;
                case 'currentIndex':
                    break;
                case 'currentPage':
                    break;
            }

            if ((option === 'displayed' || option === 'expand' || option === 'animation') && !angular.isNumber(vm.options.minWidth)) {
                setSlidesDimensions();
            }
        }

        /**
         * When sync is present it takes over
         * @param  {Number} value the value to sync with
         */
        function handleSync(value) {
            var fn;
            if (vm.options.autoplay) {
                fn = angular.isNumber(value) ? 'stop' : 'play';
                vm[fn]();
            }

            if (angular.isNumber(value)) {
                if (value > vm.slides.length - 1) vm.options.sync = vm.slides.length - 1;
                if (value < 0) vm.options.sync = 0;

                setActive();

                move(Math.floor(vm.options.sync / vm.options.perSlide), false, false);
            }
        }

        /**
         * Add the correct class to kaarousel && recalculate sizes
         */
        function setSliderDirection() {
            var currentClass = vm.options.direction === 'horizontal' ? 'vertical' : 'horizontal';

            vm.kaarousel.classList.remove('direction-' + currentClass);
            vm.kaarousel.classList.add('direction-' + vm.options.direction);

            vm.isHorizontal = vm.options.direction === 'horizontal';
            setSlidesDimensions();
        }

        /**
         * Set the options, if the option parameter is provided then
         * only this option will be changed
         * @param {String} option individual option name
         * @param {*} value  option value
         */
        function setOptions(option, value) {
            vm.options = _.merge({}, vm.defaultOptions, checkValues(getScopeOptions()));

            if (option) {
                vm.options[option] = value;
                vm.options = checkValues(vm.options);
                handleImportantChanges(option, vm.options[option]);
            } else {
                setDefaultState();
            }

            setSettings();
        }

        /**
         * Check for incoherences and fixes them
         * @param  {Obejct} options
         * @return {Object}         return the options
         */
        function checkValues(options) {
            if (options.displayed < 1) {
                options.displayed = 1;
            }
            if (options.minWidth) {
                var sliderWidth = vm.kaarouselSliderContainer.offsetWidth;
                var nbFitting = Math.floor(sliderWidth / options.minWidth);
                if (nbFitting < options.displayed) {
                    options.displayed = nbFitting;
                }
                if (options.displayed < 1) {
                    options.displayed = 1;
                }
            }
            if (!options.perSlide || options.perSlide > options.displayed) {
                options.perSlide = options.displayed;
            }
            if (options.expand && vm.slides.length < options.displayed) {
                options.displayed = vm.slides.length;
            }
            if (options.animation === animations[1] && options.perSlide !== options.displayed) {
                options.perSlide = options.displayed;
            }
            return options;
        }

        function setItemDimensions(item, index) {
            var dimension = 100 / vm.options.displayed,
                modulo = index % vm.options.displayed;

            item.element.css(vm.isHorizontal ? 'height' : 'width', '');
            item.element.css(vm.isHorizontal ? 'width' : 'height', dimension + '%');

            item.element.css(vm.isHorizontal ? 'top' : 'left', '');
            item.element.css(vm.isHorizontal ? 'left' : 'top', vm.options.animation === 'slide' ? '' : (modulo * dimension) + '%');
        }

        /**
         * Set dimensions for each slides
         */
        function setSlidesDimensions(index) {
            if (angular.isDefined(index) && vm.options.animation === 'slide') {
                setItemDimensions(vm.slides[index], index);
                return;
            }
            $timeout.cancel(vm.dimensionsTimeout);
            vm.dimensionsTimeout = $timeout(function() {
                _.forEach(vm.slides, function(slide, index) {
                    setItemDimensions(slide, index);
                });
                move(vm.currentIndex, false, true);
            }, 200);
        }

        /**
         * Set visibility settings for nav and pagination
         * Also set some state values
         */
        function setSettings() {
            if (!vm.navigation) vm.navigation = {};
            if (!vm.navigation.prev) vm.navigation.prev = {};
            if (!vm.navigation.next) vm.navigation.next = {};
            if (!vm.state) vm.state = {};
            if (!vm.pager) vm.pager = {};

            //////////////////

            var hasEnough = vm.slides.length > vm.options.displayed;

            vm.state.animating = true;
            vm.state.dragging = false;

            vm.navigation.visible = hasEnough && (!vm.options.hideNav || (vm.isHovering && vm.options.navOnHover));
            vm.navigation.prev.visible = !shouldHide('prev');
            vm.navigation.next.visible = !shouldHide('next');

            vm.pager.visible = hasEnough && (!vm.options.hidePager || (vm.isHovering && vm.options.pagerOnHover));
        }

        /**
         * Determine whether or not prev/next should be hidden
         * @param  {[type]} type [description]
         * @return {[type]}      [description]
         */
        function shouldHide(type) {
            // If looping nav is always visible
            if (vm.options.loop) {
                return false;
            }
            var response;
            switch (type) {
                case 'prev':
                    response = vm.currentIndex < vm.options.perSlide;
                    break;
                case 'next':
                    response = vm.currentIndex > (vm.slides.length - 1) - vm.options.perSlide;
                    break;
            }
            return response;
        }

        /**
         * Set watchers for scope values but also mouse events and window resize
         */
        function setWatchers() {

            // Watch changes in the options
            _.forEach($attrs, function(attribute, attributeName) {
                var debounce;
                if (vm.defaultOptions.hasOwnProperty(attributeName)) {
                    $scope.$watch(attributeName, function(nv, ov) {
                        $timeout.cancel(debounce);
                        debounce = $timeout(function() {
                            if (nv !== ov) {
                                setOptions(attributeName, nv);
                            }
                        }, 150);
                    });
                }
            });

            // On resize stop & play after it stopped
            $window.addEventListener('resize', function() {
                _.debounce(resetAfterWindowResize, 500)();
                if (vm.isPlaying) {
                    stop();
                }
            });

            // On mouse enter set isHovering & stop if pauseOnHover
            vm.kaarouselWrapper.addEventListener('mouseenter', function() {
                $timeout(function() {
                    vm.isHovering = true;
                    setSettings();

                    if (vm.options.pauseOnHover) {
                        stop();
                    }
                });
            });

            // mouse leave on the slider triggers the touchend to discard swipe
            vm.kaarouselSlider.addEventListener('mouseleave', function() {
                if (vm.state.swipable) {
                    vm.kaarouselSlider.dispatchEvent(new Event('touchend'));
                }
            });

            // On mouse leave set isHovering to false & play if autoPlay
            vm.kaarouselWrapper.addEventListener('mouseleave', function() {
                $timeout(function() {
                    vm.isHovering = false;
                    setSettings();

                    if (vm.options.autoplay && !vm.isPlaying) {
                        play();
                    }
                });
            });

            $scope.$on('$destroy', function() {
                if (vm.isPlaying) {
                    $interval.cancel(vm.interval);
                }
                angular.element(vm.kaarouselSlider).unbind('mousedown mousemove mouseup touchstart touchmove touchend touchcancel');
            });
        }

        /**
         * Re set the slide offset & play
         */
        function resetAfterWindowResize() {
            if (vm.options.minWidth) {
                setOptions();
            }

            vm.move(vm.currentIndex, false, true);

            if (vm.options.autoplay && !vm.stoppedAfterAction) {
                play();
            }
        }

        /**
         * Add a slide to the collection
         * @param  {Object} element DOM element
         */
        function register(element, index) {
            var slide = {
                element: element,
                index: index
            };

            element[0].classList.add('kaarousel-slide');

            if (!vm.slides) {
                vm.slides = [];
            }

            if (!vm.slides[index]) {
                vm.slides[index] = slide;
            } else {
                vm.slides.splice(index, 0, slide);
            }

            if (vm.ready) {
                setOptions();
                setSlidesDimensions(index);
            }
        }

        function removeSlide(index) {
            vm.slides.splice(index, 1);
            $timeout(function() {
                move(vm.currentIndex, null, true);
            }, 150);
        }

        /**
         * Set every value to default ones and set transition
         */
        function setDefaultState() {
            vm.currentIndex = 0;
            vm.currentPage = 0;

            setSlidesDimensions();
            setSliderDirection();
            setTransition();
            setAnimationClass(vm.options.animation);

            if (vm.options.autoplay && !angular.isNumber(vm.options.sync)) {
                play();
            }
            if (vm.options.swipable) {
                swipeHandler(true);
            }
            if (angular.isNumber(vm.options.sync)) {
                handleSync(vm.options.sync);
            }
        }

        /**
         * Return the active slide index when moving
         * If a index is provided it goes to the first element in the page
         * Boolean says if it should go forward or backward
         * @param  {Number/Boolean} forward index or boolean
         * @return {Number}
         */
        function getIndex(forward) {
            var index = vm.currentIndex,
                direction,
                nbSlides;

            if (angular.isNumber(forward)) {
                index = forward;
            } else {
                direction = forward ? 1 : -1;
                nbSlides = vm.slides.length - 1;

                index += vm.options.perSlide * direction;

                if (index > nbSlides) {
                    index = 0;
                }

                if (index < 0) {
                    index = Math.ceil(vm.slides.length / vm.options.perSlide) * vm.options.perSlide - vm.options.perSlide;
                }
            }
            return index;
        }

        function movePage(index) {
            move(index * vm.options.perSlide, true);
        }

        function getShift(limits) {
            var half = vm.options.displayed / 2;
            if (parseInt(half) !== half && vm.options.centerActive && getRef() >= limits.down && getRef() < limits.up) {
                return Math.floor(half);
            }
            return 0;
        }

        function getLimits() {
            var half = Math.floor(vm.options.displayed / 2);
            return {
                down: vm.options.centerActive ? half + 1 : 0,
                up: vm.options.centerActive ? vm.slides.length - half : vm.slides.length - vm.options.displayed
            };
        }

        /**
         * Determine to which slide it has to slide
         * @return {Number} Slide index
         */
        function getLastInView() {
            var index,
                ref = getRef();

            if (!vm.options.alwaysFill) {
                var half = vm.options.displayed / 2;
                if (vm.options.centerActive && ref > half) {
                    ref -= parseInt(half) !== half ? Math.floor(half) : 0;
                }
                return vm.slides[ref].element[0];
            }

            var limits = getLimits();

            if (limits.up < 0) limits.up = vm.slides.length;
            if (ref < limits.down) index = ref < limits.down ? 0 : ref;
            if (ref >= limits.down) index = ref < limits.up ? ref : vm.slides.length - vm.options.displayed;

            index -= getShift(limits);

            return vm.slides[index].element[0];
        }

        function applyStyles(offset) {

            if (vm.options.animation === 'slide') {
                var elementPos = getLastInView()[vm.isHorizontal ? 'offsetLeft' : 'offsetTop'];
                var property = vm.isHorizontal ? 'translateX' : 'translateY';
                var value = -(elementPos + (offset || 0)) + 'px';

                angular.element(vm.kaarouselSlider).css({
                    'transform': property + '(' + value + ')',
                    'height': '',
                    'width': ''
                });
            } else {

                var max;

                if (vm.options.direction === 'horizontal') {
                    max = _.max(_.filter(vm.slides, {
                        visible: true
                    }), function(slide) {
                        return slide.element[0].offsetHeight;
                    }).element[0].offsetHeight;

                    angular.element(vm.kaarouselSlider).css({
                        'height': max + 'px',
                        'transform': '',
                        'width': ''
                    });
                } else {
                    max = _.max(_.filter(vm.slides, {
                        visible: true
                    }), function(slide) {
                        return slide.element[0].offsetWidth;
                    }).element[0].offsetWidth;

                    angular.element(vm.kaarouselSlider).css({
                        'width': max + 'px',
                        'transform': '',
                        'height': ''
                    });
                }
            }
        }

        function getRef() {
            return angular.isNumber(vm.options.sync) ? vm.options.sync : vm.currentIndex;
        }

        /**
         * Set the current index & page
         * @param  {Boolean/Number}     forward  index or next
         * @param  {Boolean}            userMove is action made by user
         * @param  {replace}            replace  don't increment index just re-apply styles
         */
        function move(forward, userMove, replace) {

            if (vm.options && vm.options.beforeSlide) {
                vm.options.beforeSlide()();
            }

            vm.currentIndex = replace ? getRef() : getIndex(forward);
            vm.currentPage = Math.floor(getRef() / vm.options.perSlide);

            // Expose currentIndex and currentPage
            $scope.currentIndex = vm.currentIndex;
            $scope.currentPage = vm.currentPage;

            setActive();
            setVisible();
            applyStyles();
            setSettings();

            if (vm.currentIndex > vm.slides.length - vm.options.displayed && !vm.options.loop) {
                stop();
            }

            if (userMove && vm.isPlaying) {
                stop(!vm.options.stopAfterAction);

                if (vm.options.stopAfterAction) {
                    vm.stoppedAfterAction = true;
                }
            }

            if (vm.options.afterSlide) {
                $timeout(function() {
                    vm.options.afterSlide()();
                }, vm.options.transitionDuration);
            }
        }

        function setVisible() {
            _.forEach(vm.slides, function(slide, index) {
                var max = vm.slides.length - vm.options.displayed,
                    isVisible;

                var shift = getShift(getLimits());

                if (vm.options.animation !== 'slide') {
                    isVisible = index >= vm.currentPage * vm.options.displayed && index < (vm.currentPage + 1) * vm.options.displayed;
                } else {
                    var isEnd = getRef() > max && index >= max;
                    var ref = getRef() - shift;
                    isVisible = index >= ref && index < ref + vm.options.displayed || isEnd;
                }

                slide.visible = isVisible;
                slide.element[0].classList[isVisible ? 'add' : 'remove']('visible');
            });
        }

        /**
         * Set active class
         */
        function setActive() {
            var lastActive = _.filter(vm.slides, {
                active: true
            });

            if (lastActive.length) {
                lastActive[0].active = false;
                lastActive[0].element[0].classList.remove('active');
            }

            /////////////////////

            var index = angular.isNumber(vm.options.sync) ? vm.options.sync : vm.currentIndex;

            vm.slides[index].element[0].classList.add('active');
            vm.slides[index].active = true;
        }

        /**
         * Create interval that moves the slide
         */
        function play() {
            if (vm.isPlaying) return;

            $interval.cancel(vm.interval);

            vm.isPlaying = true;
            vm.interval = $interval(function() {
                move(true);
            }, vm.options.timeInterval);
        }

        /**
         * Cancel the play interval ( temp if relaunch )
         * @param  {Boolean} relaunch Whether or not it should restart
         */
        function stop(relaunch) {
            if (!vm.isPlaying) return;

            vm.isPlaying = false;
            $interval.cancel(vm.interval);

            if (relaunch) {
                $timeout(play, vm.options.transitionDuration);
            }
        }

        /**
         * Determine if there's enough to swipe
         * @return {Boolean}
         */
        function canSwipe() {
            return vm.options.swipable && vm.slides.length > vm.options.displayed;
        }

        /**
         * Add the transition duration property to the slider
         */
        function setTransition() {
            vm.state.animating = true;
            angular.element(vm.kaarouselSlider).css('transition-duration', vm.options.transitionDuration / 1000 + 's');
        }

        /**
         * Remove the transition duration property to the slider
         */
        function removeTransition() {
            vm.state.animating = false;
            angular.element(vm.kaarouselSlider).css('transition-duration', '');
        }

        /**
         * Add the swipe shift to current view
         * @param {Object} initial initial position
         * @param {Object} shift   current position
         */
        function addShift(initial, shift) {
            vm.kaarouselSliderContainer.classList.add('dragging');

            var offset, property = vm.options.direction === 'horizontal' ? 'x' : 'y';

            vm.state.dragging = true;

            offset = initial[property] - shift[property];

            applyStyles(offset);
        }

        /**
         * Remove all things related to the draggnig state
         */
        function removeShift() {
            vm.kaarouselSliderContainer.classList.remove('dragging');

            vm.state.animating = true;
            vm.state.dragging = false;
            setTransition();
        }

        /**
         * Determine if the shift is big enough to swipe
         * @param  {Object} startCoords start position
         * @param  {Object} lastCoords  last position
         * @return {Boolean}
         */
        function shouldSwipe(startCoords, lastCoords) {
            var property = vm.options.direction === 'horizontal' ? 'x' : 'y';
            return startCoords && lastCoords && Math.abs(startCoords[property] - lastCoords[property]) > vm.options.swipeThreshold;
        }

        /**
         * Add the swipe listener to the slider
         * toggle vm.state.swipable
         * @param  {Boolean} bind whether or not to bind
         */
        function swipeHandler(bind) {
            vm.state.swipable = bind;

            if (vm.swipeReady) return;

            var lastCoords, startCoords;

            vm.swipeReady = true;

            $swipe.bind(angular.element(vm.kaarouselSlider), {
                start: function(coords) {
                    if (!canSwipe()) {
                        return;
                    }
                    removeTransition();
                    startCoords = coords;
                    lastCoords = null;
                },
                move: function(coords) {
                    if (!canSwipe()) {
                        return;
                    }
                    lastCoords = coords;
                    addShift(startCoords, lastCoords);
                },
                end: function() {

                    removeShift();

                    if (!canSwipe() || !lastCoords) {
                        return;
                    }

                    var displacement = startCoords.x - lastCoords.x;

                    if (shouldSwipe(startCoords, lastCoords)) {
                        if (displacement > 0) {
                            // Left
                            move(true, true, false);
                        } else {
                            // right
                            move(false, true, false);
                        }
                    } else {
                        move(vm.currentIndex, true, true);
                    }
                },
                cancel: function() {
                    if (!canSwipe()) return;
                    removeShift();
                    move(vm.currentIndex, true, true);
                }
            });
        }
    }

})();

(function() {

    'use strict';

    angular
        .module('angular-kaarousel')
        .directive('kaarouselSlide', kaarouselSlide);

    /** @ngInject */
    function kaarouselSlide() {
        var directive = {
            restrict: 'EA',
            require: '^kaarousel',
            link: linkFn
        };

        return directive;

        function linkFn(scope, element, attrs, ctrl) {

            ctrl.register(element, scope.$index);

            if (scope.$last && !ctrl.ready) {
                ctrl.init();
            }

            scope.$on('$destroy', function() {
                ctrl.removeSlide(scope.$index);
            });
        }
    }

})();

// angular.module("angular-kaarousel").run(["$templateCache", function($templateCache) {$templateCache.put("app/components/kaarousel/templates/angular-kaarousel.html","<kaarousel-wrapper><kaarousel-slider-container><kaarousel-slider ng-transclude=\"\" class=\"kaarousel-slider\"></kaarousel-slider></kaarousel-slider-container><kaarousel-nav ng-class=\"{\'is-hidden\': !kc.navigation.visible}\"><kaarousel-prev ng-click=\"kc.move(null, true)\" ng-class=\"{\'is-hidden\': !kc.navigation.prev.visible}\">PREV</kaarousel-prev><kaarousel-next ng-click=\"kc.move(true, true)\" ng-class=\"{\'is-hidden\': !kc.navigation.next.visible}\">NEXT</kaarousel-next></kaarousel-nav><kaarousel-pager ng-class=\"{\'is-hidden\': !kc.pager.visible}\"><ul><li ng-repeat=\"i in kc.getPages() track by $index\" ng-click=\"kc.movePage($index)\" ng-class=\"{selected: $index === kc.currentPage}\">{{$index}}</li></ul></kaarousel-pager></kaarousel-wrapper>");}]);