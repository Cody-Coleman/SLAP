/*!
 * jQuery Simulate v@VERSION - simulate browser mouse and keyboard events
 * https://github.com/jquery/jquery-simulate
 *
 * Copyright jQuery Foundation and other contributors
 * Released under the MIT license.
 * http://jquery.org/license
 *
 * Date: @DATE
 */

;(function( $, undefined ) {

var rkeyEvent = /^key/,
	rmouseEvent = /^(?:mouse|contextmenu)|click/;

$.fn.simulate = function( type, options ) {
	return this.each(function() {
		new $.simulate( this, type, options );
	});
};

$.simulate = function( elem, type, options ) {
	var method = $.camelCase( "simulate-" + type );

	this.target = elem;
	this.options = options;

	if ( this[ method ] ) {
		this[ method ]();
	} else {
		this.simulateEvent( elem, type, options );
	}
};

$.extend( $.simulate, {

	keyCode: {
		BACKSPACE: 8,
		COMMA: 188,
		DELETE: 46,
		DOWN: 40,
		END: 35,
		ENTER: 13,
		ESCAPE: 27,
		HOME: 36,
		LEFT: 37,
		NUMPAD_ADD: 107,
		NUMPAD_DECIMAL: 110,
		NUMPAD_DIVIDE: 111,
		NUMPAD_ENTER: 108,
		NUMPAD_MULTIPLY: 106,
		NUMPAD_SUBTRACT: 109,
		PAGE_DOWN: 34,
		PAGE_UP: 33,
		PERIOD: 190,
		RIGHT: 39,
		SPACE: 32,
		TAB: 9,
		UP: 38
	},

	buttonCode: {
		LEFT: 0,
		MIDDLE: 1,
		RIGHT: 2
	}
});

$.extend( $.simulate.prototype, {

	simulateEvent: function( elem, type, options ) {
		var event = this.createEvent( type, options );
		this.dispatchEvent( elem, type, event, options );
	},

	createEvent: function( type, options ) {
		if ( rkeyEvent.test( type ) ) {
			return this.keyEvent( type, options );
		}

		if ( rmouseEvent.test( type ) ) {
			return this.mouseEvent( type, options );
		}
	},

	mouseEvent: function( type, options ) {
		var event, eventDoc, doc, body;
		options = $.extend({
			bubbles: true,
			cancelable: (type !== "mousemove"),
			view: window,
			detail: 0,
			screenX: 0,
			screenY: 0,
			clientX: 1,
			clientY: 1,
			ctrlKey: false,
			altKey: false,
			shiftKey: false,
			metaKey: false,
			button: 0,
			relatedTarget: undefined
		}, options );

		if ( document.createEvent ) {
			event = document.createEvent( "MouseEvents" );
			event.initMouseEvent( type, options.bubbles, options.cancelable,
				options.view, options.detail,
				options.screenX, options.screenY, options.clientX, options.clientY,
				options.ctrlKey, options.altKey, options.shiftKey, options.metaKey,
				options.button, options.relatedTarget || document.body.parentNode );

			// IE 9+ creates events with pageX and pageY set to 0.
			// Trying to modify the properties throws an error,
			// so we define getters to return the correct values.
			if ( event.pageX === 0 && event.pageY === 0 && Object.defineProperty ) {
				eventDoc = event.relatedTarget.ownerDocument || document;
				doc = eventDoc.documentElement;
				body = eventDoc.body;

				Object.defineProperty( event, "pageX", {
					get: function() {
						return options.clientX +
							( doc && doc.scrollLeft || body && body.scrollLeft || 0 ) -
							( doc && doc.clientLeft || body && body.clientLeft || 0 );
					}
				});
				Object.defineProperty( event, "pageY", {
					get: function() {
						return options.clientY +
							( doc && doc.scrollTop || body && body.scrollTop || 0 ) -
							( doc && doc.clientTop || body && body.clientTop || 0 );
					}
				});
			}
		} else if ( document.createEventObject ) {
			event = document.createEventObject();
			$.extend( event, options );
			// standards event.button uses constants defined here: http://msdn.microsoft.com/en-us/library/ie/ff974877(v=vs.85).aspx
			// old IE event.button uses constants defined here: http://msdn.microsoft.com/en-us/library/ie/ms533544(v=vs.85).aspx
			// so we actually need to map the standard back to oldIE
			event.button = {
				0: 1,
				1: 4,
				2: 2
			}[ event.button ] || ( event.button === -1 ? 0 : event.button );
		}

		return event;
	},

	keyEvent: function( type, options ) {
		var event;
		options = $.extend({
			bubbles: true,
			cancelable: true,
			view: window,
			ctrlKey: false,
			altKey: false,
			shiftKey: false,
			metaKey: false,
			keyCode: 0,
			charCode: undefined
		}, options );

		if ( document.createEvent ) {
			try {
				event = document.createEvent( "KeyEvents" );
				event.initKeyEvent( type, options.bubbles, options.cancelable, options.view,
					options.ctrlKey, options.altKey, options.shiftKey, options.metaKey,
					options.keyCode, options.charCode );
			// initKeyEvent throws an exception in WebKit
			// see: http://stackoverflow.com/questions/6406784/initkeyevent-keypress-only-works-in-firefox-need-a-cross-browser-solution
			// and also https://bugs.webkit.org/show_bug.cgi?id=13368
			// fall back to a generic event until we decide to implement initKeyboardEvent
			} catch( err ) {
				event = document.createEvent( "Events" );
				event.initEvent( type, options.bubbles, options.cancelable );
				$.extend( event, {
					view: options.view,
					ctrlKey: options.ctrlKey,
					altKey: options.altKey,
					shiftKey: options.shiftKey,
					metaKey: options.metaKey,
					keyCode: options.keyCode,
					charCode: options.charCode
				});
			}
		} else if ( document.createEventObject ) {
			event = document.createEventObject();
			$.extend( event, options );
		}

		if ( !!/msie [\w.]+/.exec( navigator.userAgent.toLowerCase() ) || (({}).toString.call( window.opera ) === "[object Opera]") ) {
			event.keyCode = (options.charCode > 0) ? options.charCode : options.keyCode;
			event.charCode = undefined;
		}

		return event;
	},

	dispatchEvent: function( elem, type, event ) {
		if ( elem[ type ] ) {
			elem[ type ]();
		} else if ( elem.dispatchEvent ) {
			elem.dispatchEvent( event );
		} else if ( elem.fireEvent ) {
			elem.fireEvent( "on" + type, event );
		}
	},

	simulateFocus: function() {
		var focusinEvent,
			triggered = false,
			element = $( this.target );

		function trigger() {
			triggered = true;
		}

		element.bind( "focus", trigger );
		element[ 0 ].focus();

		if ( !triggered ) {
			focusinEvent = $.Event( "focusin" );
			focusinEvent.preventDefault();
			element.trigger( focusinEvent );
			element.triggerHandler( "focus" );
		}
		element.unbind( "focus", trigger );
	},

	simulateBlur: function() {
		var focusoutEvent,
			triggered = false,
			element = $( this.target );

		function trigger() {
			triggered = true;
		}

		element.bind( "blur", trigger );
		element[ 0 ].blur();

		// blur events are async in IE
		setTimeout(function() {
			// IE won't let the blur occur if the window is inactive
			if ( element[ 0 ].ownerDocument.activeElement === element[ 0 ] ) {
				element[ 0 ].ownerDocument.body.focus();
			}

			// Firefox won't trigger events if the window is inactive
			// IE doesn't trigger events if we had to manually focus the body
			if ( !triggered ) {
				focusoutEvent = $.Event( "focusout" );
				focusoutEvent.preventDefault();
				element.trigger( focusoutEvent );
				element.triggerHandler( "blur" );
			}
			element.unbind( "blur", trigger );
		}, 1 );
	}
});



/** complex events **/

function findCenter( elem ) {
	var offset,
		document = $( elem.ownerDocument );
	elem = $( elem );
	offset = elem.offset();

	return {
		x: offset.left + elem.outerWidth() / 2 - document.scrollLeft(),
		y: offset.top + elem.outerHeight() / 2 - document.scrollTop()
	};
}

function findCorner( elem ) {
	var offset,
		document = $( elem.ownerDocument );
	elem = $( elem );
	offset = elem.offset();

	return {
		x: offset.left - document.scrollLeft(),
		y: offset.top - document.scrollTop()
	};
}

$.extend( $.simulate.prototype, {
	simulateDrag: function() {
		var i = 0,
			target = this.target,
			eventDoc = target.ownerDocument,
			options = this.options,
			center = options.handle === "corner" ? findCorner( target ) : findCenter( target ),
			x = Math.floor( center.x ),
			y = Math.floor( center.y ),
			coord = { clientX: x, clientY: y },
			dx = options.dx || ( options.x !== undefined ? options.x - x : 0 ),
			dy = options.dy || ( options.y !== undefined ? options.y - y : 0 ),
			moves = options.moves || 3;

		this.simulateEvent( target, "mousedown", coord );

		for ( ; i < moves ; i++ ) {
			x += dx / moves;
			y += dy / moves;

			coord = {
				clientX: Math.round( x ),
				clientY: Math.round( y )
			};

			this.simulateEvent( eventDoc, "mousemove", coord );
		}

		if ( $.contains( eventDoc, target ) ) {
			this.simulateEvent( target, "mouseup", coord );
			this.simulateEvent( target, "click", coord );
		} else {
			this.simulateEvent( eventDoc, "mouseup", coord );
		}
	}
});

})( jQuery );

/*jshint camelcase:true, plusplus:true, forin:true, noarg:true, noempty:true, eqeqeq:true, bitwise:true, strict:true, undef:true, unused:true, curly:true, browser:true, devel:true, maxerr:100, white:false, onevar:false */
/*global jQuery:true $:true */

/* jQuery Simulate Extended Plugin 1.3.0
 * http://github.com/j-ulrich/jquery-simulate-ext
 *
 * Copyright (c) 2014 Jochen Ulrich
 * Licensed under the MIT license (MIT-LICENSE.txt).
 */

;(function( $ ) {
	"use strict";

	/* Overwrite the $.simulate.prototype.mouseEvent function
	 * to convert pageX/Y to clientX/Y
	 */
	var originalMouseEvent = $.simulate.prototype.mouseEvent,
		rdocument = /\[object (?:HTML)?Document\]/;

	$.simulate.prototype.mouseEvent = function(type, options) {
		if (options.pageX || options.pageY) {
			var doc = rdocument.test(Object.prototype.toString.call(this.target))? this.target : (this.target.ownerDocument || document);
			options.clientX = (options.pageX || 0) - $(doc).scrollLeft();
			options.clientY = (options.pageY || 0) - $(doc).scrollTop();
		}
		return originalMouseEvent.apply(this, [type, options]);
	};


})( jQuery );

/*!
 * jQuery Simulate v@VERSION - simulate browser mouse and keyboard events
 * https://github.com/jquery/jquery-simulate
 *
 * Copyright jQuery Foundation and other contributors
 * Released under the MIT license.
 * http://jquery.org/license
 *
 * Date: @DATE
 */

;(function( $, undefined ) {

var rkeyEvent = /^key/,
	rmouseEvent = /^(?:mouse|contextmenu)|click/;

$.fn.simulate = function( type, options ) {
	return this.each(function() {
		new $.simulate( this, type, options );
	});
};

$.simulate = function( elem, type, options ) {
	var method = $.camelCase( "simulate-" + type );

	this.target = elem;
	this.options = options;

	if ( this[ method ] ) {
		this[ method ]();
	} else {
		this.simulateEvent( elem, type, options );
	}
};

$.extend( $.simulate, {

	keyCode: {
		BACKSPACE: 8,
		COMMA: 188,
		DELETE: 46,
		DOWN: 40,
		END: 35,
		ENTER: 13,
		ESCAPE: 27,
		HOME: 36,
		LEFT: 37,
		NUMPAD_ADD: 107,
		NUMPAD_DECIMAL: 110,
		NUMPAD_DIVIDE: 111,
		NUMPAD_ENTER: 108,
		NUMPAD_MULTIPLY: 106,
		NUMPAD_SUBTRACT: 109,
		PAGE_DOWN: 34,
		PAGE_UP: 33,
		PERIOD: 190,
		RIGHT: 39,
		SPACE: 32,
		TAB: 9,
		UP: 38
	},

	buttonCode: {
		LEFT: 0,
		MIDDLE: 1,
		RIGHT: 2
	}
});

$.extend( $.simulate.prototype, {

	simulateEvent: function( elem, type, options ) {
		var event = this.createEvent( type, options );
		this.dispatchEvent( elem, type, event, options );
	},

	createEvent: function( type, options ) {
		if ( rkeyEvent.test( type ) ) {
			return this.keyEvent( type, options );
		}

		if ( rmouseEvent.test( type ) ) {
			return this.mouseEvent( type, options );
		}
	},

	mouseEvent: function( type, options ) {
		var event, eventDoc, doc, body;
		options = $.extend({
			bubbles: true,
			cancelable: (type !== "mousemove"),
			view: window,
			detail: 0,
			screenX: 0,
			screenY: 0,
			clientX: 1,
			clientY: 1,
			ctrlKey: false,
			altKey: false,
			shiftKey: false,
			metaKey: false,
			button: 0,
			relatedTarget: undefined
		}, options );

		if ( document.createEvent ) {
			event = document.createEvent( "MouseEvents" );
			event.initMouseEvent( type, options.bubbles, options.cancelable,
				options.view, options.detail,
				options.screenX, options.screenY, options.clientX, options.clientY,
				options.ctrlKey, options.altKey, options.shiftKey, options.metaKey,
				options.button, options.relatedTarget || document.body.parentNode );

			// IE 9+ creates events with pageX and pageY set to 0.
			// Trying to modify the properties throws an error,
			// so we define getters to return the correct values.
			if ( event.pageX === 0 && event.pageY === 0 && Object.defineProperty ) {
				eventDoc = event.relatedTarget.ownerDocument || document;
				doc = eventDoc.documentElement;
				body = eventDoc.body;

				Object.defineProperty( event, "pageX", {
					get: function() {
						return options.clientX +
							( doc && doc.scrollLeft || body && body.scrollLeft || 0 ) -
							( doc && doc.clientLeft || body && body.clientLeft || 0 );
					}
				});
				Object.defineProperty( event, "pageY", {
					get: function() {
						return options.clientY +
							( doc && doc.scrollTop || body && body.scrollTop || 0 ) -
							( doc && doc.clientTop || body && body.clientTop || 0 );
					}
				});
			}
		} else if ( document.createEventObject ) {
			event = document.createEventObject();
			$.extend( event, options );
			// standards event.button uses constants defined here: http://msdn.microsoft.com/en-us/library/ie/ff974877(v=vs.85).aspx
			// old IE event.button uses constants defined here: http://msdn.microsoft.com/en-us/library/ie/ms533544(v=vs.85).aspx
			// so we actually need to map the standard back to oldIE
			event.button = {
				0: 1,
				1: 4,
				2: 2
			}[ event.button ] || ( event.button === -1 ? 0 : event.button );
		}

		return event;
	},

	keyEvent: function( type, options ) {
		var event;
		options = $.extend({
			bubbles: true,
			cancelable: true,
			view: window,
			ctrlKey: false,
			altKey: false,
			shiftKey: false,
			metaKey: false,
			keyCode: 0,
			charCode: undefined
		}, options );

		if ( document.createEvent ) {
			try {
				event = document.createEvent( "KeyEvents" );
				event.initKeyEvent( type, options.bubbles, options.cancelable, options.view,
					options.ctrlKey, options.altKey, options.shiftKey, options.metaKey,
					options.keyCode, options.charCode );
			// initKeyEvent throws an exception in WebKit
			// see: http://stackoverflow.com/questions/6406784/initkeyevent-keypress-only-works-in-firefox-need-a-cross-browser-solution
			// and also https://bugs.webkit.org/show_bug.cgi?id=13368
			// fall back to a generic event until we decide to implement initKeyboardEvent
			} catch( err ) {
				event = document.createEvent( "Events" );
				event.initEvent( type, options.bubbles, options.cancelable );
				$.extend( event, {
					view: options.view,
					ctrlKey: options.ctrlKey,
					altKey: options.altKey,
					shiftKey: options.shiftKey,
					metaKey: options.metaKey,
					keyCode: options.keyCode,
					charCode: options.charCode
				});
			}
		} else if ( document.createEventObject ) {
			event = document.createEventObject();
			$.extend( event, options );
		}

		if ( !!/msie [\w.]+/.exec( navigator.userAgent.toLowerCase() ) || (({}).toString.call( window.opera ) === "[object Opera]") ) {
			event.keyCode = (options.charCode > 0) ? options.charCode : options.keyCode;
			event.charCode = undefined;
		}

		return event;
	},

	dispatchEvent: function( elem, type, event ) {
		if ( elem[ type ] ) {
			elem[ type ]();
		} else if ( elem.dispatchEvent ) {
			elem.dispatchEvent( event );
		} else if ( elem.fireEvent ) {
			elem.fireEvent( "on" + type, event );
		}
	},

	simulateFocus: function() {
		var focusinEvent,
			triggered = false,
			element = $( this.target );

		function trigger() {
			triggered = true;
		}

		element.bind( "focus", trigger );
		element[ 0 ].focus();

		if ( !triggered ) {
			focusinEvent = $.Event( "focusin" );
			focusinEvent.preventDefault();
			element.trigger( focusinEvent );
			element.triggerHandler( "focus" );
		}
		element.unbind( "focus", trigger );
	},

	simulateBlur: function() {
		var focusoutEvent,
			triggered = false,
			element = $( this.target );

		function trigger() {
			triggered = true;
		}

		element.bind( "blur", trigger );
		element[ 0 ].blur();

		// blur events are async in IE
		setTimeout(function() {
			// IE won't let the blur occur if the window is inactive
			if ( element[ 0 ].ownerDocument.activeElement === element[ 0 ] ) {
				element[ 0 ].ownerDocument.body.focus();
			}

			// Firefox won't trigger events if the window is inactive
			// IE doesn't trigger events if we had to manually focus the body
			if ( !triggered ) {
				focusoutEvent = $.Event( "focusout" );
				focusoutEvent.preventDefault();
				element.trigger( focusoutEvent );
				element.triggerHandler( "blur" );
			}
			element.unbind( "blur", trigger );
		}, 1 );
	}
});



/** complex events **/

function findCenter( elem ) {
	var offset,
		document = $( elem.ownerDocument );
	elem = $( elem );
	offset = elem.offset();

	return {
		x: offset.left + elem.outerWidth() / 2 - document.scrollLeft(),
		y: offset.top + elem.outerHeight() / 2 - document.scrollTop()
	};
}

function findCorner( elem ) {
	var offset,
		document = $( elem.ownerDocument );
	elem = $( elem );
	offset = elem.offset();

	return {
		x: offset.left - document.scrollLeft(),
		y: offset.top - document.scrollTop()
	};
}

$.extend( $.simulate.prototype, {
	simulateDrag: function() {
		var i = 0,
			target = this.target,
			eventDoc = target.ownerDocument,
			options = this.options,
			center = options.handle === "corner" ? findCorner( target ) : findCenter( target ),
			x = Math.floor( center.x ),
			y = Math.floor( center.y ),
			coord = { clientX: x, clientY: y },
			dx = options.dx || ( options.x !== undefined ? options.x - x : 0 ),
			dy = options.dy || ( options.y !== undefined ? options.y - y : 0 ),
			moves = options.moves || 3;

		this.simulateEvent( target, "mousedown", coord );

		for ( ; i < moves ; i++ ) {
			x += dx / moves;
			y += dy / moves;

			coord = {
				clientX: Math.round( x ),
				clientY: Math.round( y )
			};

			this.simulateEvent( eventDoc, "mousemove", coord );
		}

		if ( $.contains( eventDoc, target ) ) {
			this.simulateEvent( target, "mouseup", coord );
			this.simulateEvent( target, "click", coord );
		} else {
			this.simulateEvent( eventDoc, "mouseup", coord );
		}
	}
});

})( jQuery );

/*jshint camelcase:true, plusplus:true, forin:true, noarg:true, noempty:true, eqeqeq:true, bitwise:true, strict:true, undef:true, unused:true, curly:true, browser:true, devel:true, maxerr:100, white:false, onevar:false */
/*global jQuery:true $:true */

/* jQuery Simulate Extended Plugin 1.3.0
 * http://github.com/j-ulrich/jquery-simulate-ext
 *
 * Copyright (c) 2014 Jochen Ulrich
 * Licensed under the MIT license (MIT-LICENSE.txt).
 */

;(function( $ ) {
	"use strict";

	/* Overwrite the $.simulate.prototype.mouseEvent function
	 * to convert pageX/Y to clientX/Y
	 */
	var originalMouseEvent = $.simulate.prototype.mouseEvent,
		rdocument = /\[object (?:HTML)?Document\]/;

	$.simulate.prototype.mouseEvent = function(type, options) {
		if (options.pageX || options.pageY) {
			var doc = rdocument.test(Object.prototype.toString.call(this.target))? this.target : (this.target.ownerDocument || document);
			options.clientX = (options.pageX || 0) - $(doc).scrollLeft();
			options.clientY = (options.pageY || 0) - $(doc).scrollTop();
		}
		return originalMouseEvent.apply(this, [type, options]);
	};


})( jQuery );

/*jshint camelcase:true, plusplus:true, forin:true, noarg:true, noempty:true, eqeqeq:true, bitwise:true, strict:true, undef:true, unused:true, curly:true, browser:true, devel:true, maxerr:100, white:false, onevar:false */
/*global jQuery:true $:true */

/* jQuery Simulate Drag-n-Drop Plugin 1.3.0
 * http://github.com/j-ulrich/jquery-simulate-ext
 *
 * Copyright (c) 2014 Jochen Ulrich
 * Licensed under the MIT license (MIT-LICENSE.txt).
 */

;(function($, undefined) {
	"use strict";

	/* Overwrite the $.fn.simulate function to reduce the jQuery set to the first element for the
	 * drag-n-drop interactions.
	 */
	$.fn.simulate = function( type, options ) {
		switch (type) {
		case "drag":
		case "drop":
		case "drag-n-drop":
			var ele = this.first();
			new $.simulate( ele[0], type, options);
			return ele;
		default:
			return this.each(function() {
				new $.simulate( this, type, options );
			});
		}
	};

	var now = Date.now || function() { return new Date().getTime(); };

	var rdocument = /\[object (?:HTML)?Document\]/;
	/**
	 * Tests whether an object is an (HTML) document object.
	 * @param {DOM Element} elem - the object/element to be tested
	 * @returns {Boolean} <code>true</code> if <i>elem</i> is an (HTML) document object.
	 * @private
	 * @author julrich
	 * @since 1.1
	 */
	function isDocument( elem ) {
		return rdocument.test(Object.prototype.toString.call($(elem)[0]));
	}

	/**
	 * Selects the first match from an array.
	 * @param {Array} array - Array of objects to be be tested
	 * @param {Function} check - Callback function that accepts one argument (which will be one element
	 * from the <i>array</i>) and returns a boolean.
	 * @returns {Boolean|null} the first element in <i>array</i> for which <i>check</i> returns <code>true</code>.
	 * If none of the elements in <i>array</i> passes <i>check</i>, <code>null</code> is returned.
	 * @private
	 * @author julrich
	 * @since 1.1
	 */
	function selectFirstMatch(array, check) {
		var i;
		if ($.isFunction(check)) {
			for (i=0; i < array.length; i+=1) {
				if (check(array[i])) {
					return array[i];
				}
			}
			return null;
		}
		else {
			for (i=0; i < array.length; i+=1) {
				if (array[i]) {
					return array[i];
				}
			}
			return null;
		}
	}

	// Based on the findCenter function from jquery.simulate.js
	/**
	 * Calculates the position of the center of an DOM element.
	 * @param {DOM Element} elem - the element whose center should be calculated.
	 * @returns {Object} an object with the properties <code>x</code> and <code>y</code>
	 * representing the position of the center of <i>elem</i> in page relative coordinates
	 * (i.e. independent of any scrolling).
	 * @private
	 * @author julrich
	 * @since 1.0
	 */
	function findCenter( elem ) {
		var offset,
			$elem = $( elem );
		if ( isDocument($elem[0]) ) {
			offset = {left: 0, top: 0};
		}
		else {
			offset = $elem.offset();
		}

		return {
			x: offset.left + $elem.outerWidth() / 2,
			y: offset.top + $elem.outerHeight() / 2
		};
	}

	/**
	 * Converts page relative coordinates into client relative coordinates.
	 * @param {Numeric|Object} x - Either the x coordinate of the page relative coordinates or
	 * an object with the properties <code>pageX</code> and <code>pageY</code> representing page
	 * relative coordinates.
	 * @param {Numeric} [y] - If <i>x</i> is numeric (i.e. the x coordinate of page relative coordinates),
	 * then this is the y coordinate. If <i>x</i> is an object, this parameter is skipped.
	 * @param {DOM Document} [docRel] - Optional DOM document object used to calculate the client relative
	 * coordinates. The page relative coordinates are interpreted as being relative to that document and
	 * the scroll position of that document is used to calculate the client relative coordinates.
	 * By default, <code>document</code> is used.
	 * @returns {Object} an object representing the client relative coordinates corresponding to the
	 * given page relative coordinates. The object either provides the properties <code>x</code> and
	 * <code>y</code> when <i>x</i> and <i>y</i> were given as arguments, or <code>clientX</code>
	 * and <code>clientY</code> when the parameter <i>x</i> was given as an object (see above).
	 * @private
	 * @author julrich
	 * @since 1.0
	 */
	function pageToClientPos(x, y, docRel) {
		var $document;
		if ( isDocument(y) ) {
			$document = $(y);
		} else {
			$document = $(docRel || document);
		}

		if (typeof x === "number" && typeof y === "number") {
			return {
				x: x - $document.scrollLeft(),
				y: y - $document.scrollTop()
			};
		}
		else if (typeof x === "object" && x.pageX && x.pageY) {
			return {
				clientX: x.pageX - $document.scrollLeft(),
				clientY: x.pageY - $document.scrollTop()
			};
		}
	}

	/**
	 * Browser-independent implementation of <code>document.elementFromPoint()</code>.
	 *
	 * When run for the first time on a scrolled page, this function performs a check on how
	 * <code>document.elementFromPoint()</code> is implemented in the current browser. It stores
	 * the results in two static variables so that the check can be skipped for successive calls.
	 *
	 * @param {Numeric|Object} x - Either the x coordinate of client relative coordinates or an object
	 * with the properties <code>x</code> and <code>y</code> representing client relative coordinates.
	 * @param {Numeric} [y] - If <i>x</i> is numeric (i.e. the x coordinate of client relative coordinates),
	 * this is the y coordinate. If <i>x</i> is an object, this parameter is skipped.
	 * @param {DOM Document} [docRel] - Optional DOM document object
	 * @returns {DOM Element|Null}
	 * @private
	 * @author Nicolas Zeh (Basic idea), julrich
	 * @see http://www.zehnet.de/2010/11/19/document-elementfrompoint-a-jquery-solution/
	 * @since 1.0
	 */
	function elementAtPosition(x, y, docRel) {
		var doc;
		if ( isDocument(y) ) {
			doc = y;
		} else {
			doc = docRel || document;
		}

		if(!doc.elementFromPoint) {
			return null;
		}

		var clientX = x, clientY = y;
		if (typeof x === "object" && (x.clientX || x.clientY)) {
			clientX = x.clientX || 0 ;
			clientY = x.clientY || 0;
		}

		if(elementAtPosition.prototype.check)
		{
			var sl, ele;
			if ((sl = $(doc).scrollTop()) >0)
			{
				ele = doc.elementFromPoint(0, sl + $(window).height() -1);
				if ( ele !== null && ele.tagName.toUpperCase() === 'HTML' ) { ele = null; }
				elementAtPosition.prototype.nativeUsesRelative = ( ele === null );
			}
			else if((sl = $(doc).scrollLeft()) >0)
			{
				ele = doc.elementFromPoint(sl + $(window).width() -1, 0);
				if ( ele !== null && ele.tagName.toUpperCase() === 'HTML' ) { ele = null; }
				elementAtPosition.prototype.nativeUsesRelative = ( ele === null );
			}
			elementAtPosition.prototype.check = (sl<=0); // Check was not meaningful because we were at scroll position 0
		}

		if(!elementAtPosition.prototype.nativeUsesRelative)
		{
			clientX += $(doc).scrollLeft();
			clientY += $(doc).scrollTop();
		}

		return doc.elementFromPoint(clientX,clientY);
	}
	// Default values for the check variables
	elementAtPosition.prototype.check = true;
	elementAtPosition.prototype.nativeUsesRelative = true;

	/**
	 * Informs the rest of the world that the drag is finished.
	 * @param {DOM Element} ele - The element which was dragged.
	 * @param {Object} [options] - The drag options.
	 * @fires simulate-drag
	 * @private
	 * @author julrich
	 * @since 1.0
	 */
	function dragFinished(ele, options) {
		var opts = options || {};
		$(ele).trigger({type: "simulate-drag"});
		if ($.isFunction(opts.callback)) {
			opts.callback.apply(ele);
		}
	}

	/**
	 * Generates a series of <code>mousemove</code> events for a drag.
	 * @param {Object} self - The simulate object.
	 * @param {DOM Element} ele - The element which is dragged.
	 * @param {Object} start - The start coordinates of the drag, represented using the properties
	 * <code>x</code> and <code>y</code>.
	 * @param {Object} drag - The distance to be dragged, represented using the properties <code>dx</code>
	 * and <code>dy</code>.
	 * @param {Object} options - The drag options. Must have the property <code>interpolation</code>
	 * containing the interpolation options (<code>stepWidth</code>, <code>stepCount</code>, etc.).
	 * @requires eventTarget
	 * @requires now()
	 * @private
	 * @author julrich
	 * @since 1.0
	 */
	function interpolatedEvents(self, ele, start, drag, options) {
		var targetDoc = selectFirstMatch([ele, ele.ownerDocument], isDocument) || document,
			interpolOptions = options.interpolation,
			dragDistance = Math.sqrt(Math.pow(drag.dx,2) + Math.pow(drag.dy,2)), // sqrt(a^2 + b^2)
			stepWidth, stepCount, stepVector;

		if (interpolOptions.stepWidth) {
			stepWidth = parseInt(interpolOptions.stepWidth, 10);
			stepCount = Math.floor(dragDistance / stepWidth)-1;
			var stepScale = stepWidth / dragDistance;
			stepVector = {x: drag.dx*stepScale, y: drag.dy*stepScale };
		}
		else {
			stepCount = parseInt(interpolOptions.stepCount, 10);
			stepWidth = dragDistance / (stepCount+1);
			stepVector = {x: drag.dx/(stepCount+1), y: drag.dy/(stepCount+1)};
		}


		var coords = $.extend({},start);

		/**
		 * Calculates the effective coordinates for one <code>mousemove</code> event and fires the event.
		 * @requires eventTarget
		 * @requires targetDoc
		 * @requires coords
		 * @requires stepVector
		 * @requires interpolOptions
		 * @fires mousemove
		 * @inner
		 * @author julrich
		 * @since 1.0
		 */
		function interpolationStep() {
			coords.x += stepVector.x;
			coords.y += stepVector.y;
			var effectiveCoords = {pageX: coords.x, pageY: coords.y};
			if (interpolOptions.shaky && (interpolOptions.shaky === true || !isNaN(parseInt(interpolOptions.shaky,10)) )) {
				var amplitude = (interpolOptions.shaky === true)? 1 : parseInt(interpolOptions.shaky,10);
				effectiveCoords.pageX += Math.floor(Math.random()*(2*amplitude+1)-amplitude);
				effectiveCoords.pageY += Math.floor(Math.random()*(2*amplitude+1)-amplitude);
			}
			var clientCoord = pageToClientPos(effectiveCoords, targetDoc),
				eventTarget = elementAtPosition(clientCoord, targetDoc) || ele;
			self.simulateEvent( eventTarget, "mousemove", {pageX: Math.round(effectiveCoords.pageX), pageY: Math.round(effectiveCoords.pageY)});
		}


		var lastTime;

		/**
		 * Performs one interpolation step (i.e. cares about firing the event) and then sleeps for
		 * <code>stepDelay</code> milliseconds.
		 * @requires lastTime
		 * @requires stepDelay
		 * @requires step
		 * @requires ele
		 * @requires eventTarget
		 * @reuiqre targetDoc
		 * @requires start
		 * @requires drag
		 * @requires now()
		 * @inner
		 * @author julrich
		 * @since 1.0
		 */
		function stepAndSleep() {
			var timeElapsed = now() - lastTime; // Work-around for Firefox & IE "bug": setTimeout can fire before the timeout
			if (timeElapsed >= stepDelay) {
				if (step < stepCount) {
					interpolationStep();
					step += 1;
					lastTime = now();
					setTimeout(stepAndSleep, stepDelay);
				}
				else {
					var pageCoord = {pageX: Math.round(start.x+drag.dx), pageY: Math.round(start.y+drag.dy)},
						clientCoord = pageToClientPos(pageCoord, targetDoc),
						eventTarget = elementAtPosition(clientCoord, targetDoc) || ele;
					self.simulateEvent( eventTarget, "mousemove", pageCoord);
					dragFinished(ele, options);
				}
			}
			else {
				setTimeout(stepAndSleep, stepDelay - timeElapsed);
			}

		}

		if ( (!interpolOptions.stepDelay && !interpolOptions.duration) || ((interpolOptions.stepDelay <= 0) && (interpolOptions.duration <= 0)) ) {
			// Trigger as fast as possible
			for (var i=0; i < stepCount; i+=1) {
				interpolationStep();
			}
			var pageCoord = {pageX: Math.round(start.x+drag.dx), pageY: Math.round(start.y+drag.dy)},
				clientCoord = pageToClientPos(pageCoord, targetDoc),
				eventTarget = elementAtPosition(clientCoord, targetDoc) || ele;
			self.simulateEvent( eventTarget, "mousemove", pageCoord);
			dragFinished(ele, options);
		}
		else {
			var stepDelay = parseInt(interpolOptions.stepDelay,10) || Math.ceil(parseInt(interpolOptions.duration,10) / (stepCount+1));
			var step = 0;

			lastTime = now();
			setTimeout(stepAndSleep, stepDelay);
		}

	}

	/**
	 * @returns {Object|undefined} an object containing information about the currently active drag
	 * or <code>undefined</code> when there is no active drag.
	 * The returned object contains the following properties:
	 * <ul>
	 *     <li><code>dragElement</code>: the dragged element</li>
	 *     <li><code>dragStart</code>: object with the properties <code>x</code> and <code>y</code>
	 * representing the page relative start coordinates of the drag</li>
	 *     <li><code>dragDistance</code>: object with the properties <code>x</code> and <code>y</code>
	 * representing the distance of the drag in x and y direction</li>
	 * </ul>
	 * @public
	 * @author julrich
	 * @since 1.0
	 */
	$.simulate.activeDrag = function() {
		if (!$.simulate._activeDrag) {
			return undefined;
		}
		return $.extend(true,{},$.simulate._activeDrag);
	};

	$.extend( $.simulate.prototype,

	/**
	 * @lends $.simulate.prototype
	 */
	{


		/**
		 * Simulates a drag.
		 *
		 * @see https://github.com/j-ulrich/jquery-simulate-ext/blob/master/doc/drag-n-drop.md
		 * @public
		 * @author julrich
		 * @since 1.0
		 */
		simulateDrag: function() {
			var self = this,
				ele = self.target,
				options = $.extend({
					dx: 0,
					dy: 0,
					dragTarget: undefined,
					clickToDrag: false,
					eventProps: {},
					interpolation: {
						stepWidth: 0,
						stepCount: 0,
						stepDelay: 0,
						duration: 0,
						shaky: false
					},
					callback: undefined
				},	this.options);

			var start,
				continueDrag = ($.simulate._activeDrag && $.simulate._activeDrag.dragElement === ele);

			if (continueDrag) {
				start = $.simulate._activeDrag.dragStart;
			}
			else {
				start = findCenter( ele );
			}

			var x = Math.round( start.x ),
				y = Math.round( start.y ),
				coord = { pageX: x, pageY: y },
				dx,
				dy;

			if (options.dragTarget) {
				var end = findCenter(options.dragTarget);
				dx = Math.round(end.x - start.x);
				dy = Math.round(end.y - start.y);
			}
			else {
				dx = options.dx || 0;
				dy = options.dy || 0;
			}

			if (continueDrag) {
				// We just continue to move the dragged element
				$.simulate._activeDrag.dragDistance.x += dx;
				$.simulate._activeDrag.dragDistance.y += dy;
				coord = { pageX: Math.round(x + $.simulate._activeDrag.dragDistance.x) , pageY: Math.round(y + $.simulate._activeDrag.dragDistance.y) };
			}
			else {
				if ($.simulate._activeDrag) {
					// Drop before starting a new drag
					$($.simulate._activeDrag.dragElement).simulate( "drop" );
				}

				// We start a new drag
				$.extend(options.eventProps, coord);
				self.simulateEvent( ele, "mousedown", options.eventProps );
				if (options.clickToDrag === true) {
					self.simulateEvent( ele, "mouseup", options.eventProps );
					self.simulateEvent( ele, "click", options.eventProps );
				}
				$(ele).add(ele.ownerDocument).one('mouseup', function() {
					$.simulate._activeDrag = undefined;
				});

				$.extend($.simulate, {
					_activeDrag: {
						dragElement: ele,
						dragStart: { x: x, y: y },
						dragDistance: { x: dx, y: dy }
					}
				});
				coord = { pageX: Math.round(x + dx), pageY: Math.round(y + dy) };
			}

			if (dx !== 0 || dy !== 0) {

				if ( options.interpolation && (options.interpolation.stepCount || options.interpolation.stepWidth) ) {
					interpolatedEvents(self, ele, {x: x, y: y}, {dx: dx, dy: dy}, options);
				}
				else {
					var targetDoc = selectFirstMatch([ele, ele.ownerDocument], isDocument) || document,
						clientCoord = pageToClientPos(coord, targetDoc),
						eventTarget = elementAtPosition(clientCoord, targetDoc) || ele;

					$.extend(options.eventProps, coord);
					self.simulateEvent( eventTarget, "mousemove", options.eventProps );
					dragFinished(ele, options);
				}
			}
			else {
				dragFinished(ele, options);
			}
		},

		/**
		 * Simulates a drop.
		 *
		 * @see https://github.com/j-ulrich/jquery-simulate-ext/blob/master/doc/drag-n-drop.md
		 * @public
		 * @author julrich
		 * @since 1.0
		 */
		simulateDrop: function() {
			var self = this,
				ele = this.target,
				activeDrag = $.simulate._activeDrag,
				options = $.extend({
					clickToDrop: false,
					eventProps: {},
					callback: undefined
				}, self.options),
				moveBeforeDrop = true,
				center = findCenter( ele ),
				x = Math.round( center.x ),
				y = Math.round( center.y ),
				coord = { pageX: x, pageY: y },
				targetDoc = ( (activeDrag)? selectFirstMatch([activeDrag.dragElement, activeDrag.dragElement.ownerDocument], isDocument) : selectFirstMatch([ele, ele.ownerDocument], isDocument) ) || document,
				clientCoord = pageToClientPos(coord, targetDoc),
				eventTarget = elementAtPosition(clientCoord, targetDoc);

			if (activeDrag && (activeDrag.dragElement === ele || isDocument(ele))) {
				// We already moved the mouse during the drag so we just simulate the drop on the end position
				x = Math.round(activeDrag.dragStart.x + activeDrag.dragDistance.x);
				y = Math.round(activeDrag.dragStart.y + activeDrag.dragDistance.y);
				coord = { pageX: x, pageY: y };
				clientCoord = pageToClientPos(coord, targetDoc);
				eventTarget = elementAtPosition(clientCoord, targetDoc);
				moveBeforeDrop = false;
			}

			if (!eventTarget) {
				eventTarget = (activeDrag)? activeDrag.dragElement : ele;
			}

			$.extend(options.eventProps, coord);

			if (moveBeforeDrop === true) {
				// Else we assume the drop should happen on target, so we move there
				self.simulateEvent( eventTarget, "mousemove", options.eventProps );
			}

			if (options.clickToDrop) {
				self.simulateEvent( eventTarget, "mousedown", options.eventProps );
			}
			this.simulateEvent( eventTarget, "mouseup", options.eventProps );
			if (options.clickToDrop) {
				self.simulateEvent( eventTarget, "click", options.eventProps );
			}

			$.simulate._activeDrag = undefined;
			$(eventTarget).trigger({type: "simulate-drop"});
			if ($.isFunction(options.callback)) {
				options.callback.apply(eventTarget);
			}
		},

		/**
		 * Simulates a drag followed by drop.
		 *
		 * @see https://github.com/j-ulrich/jquery-simulate-ext/blob/master/doc/drag-n-drop.md
		 * @public
		 * @author julrich
		 * @since 1.0
		 */
		simulateDragNDrop: function() {
			var self = this,
				ele = this.target,
				options = $.extend({
					dragTarget: undefined,
					dropTarget: undefined
				}, self.options),
				// If there is a dragTarget or dx/dy, then we drag there and simulate an independent drop on dropTarget or ele
				dropEle = ((options.dragTarget || options.dx || options.dy)? options.dropTarget : ele) || ele;
/*
				dx = (options.dropTarget)? 0 : (options.dx || 0),
				dy = (options.dropTarget)? 0 : (options.dy || 0),
				dragDistance = { dx: dx, dy: dy };

			$.extend(options, dragDistance);
*/
			$(ele).simulate( "drag", $.extend({},options,{
				// If there is no dragTarget, no dx and no dy, we drag onto the dropTarget directly
				dragTarget: options.dragTarget || ((options.dx || options.dy)?undefined:options.dropTarget),
				callback: function() {
					$(dropEle).simulate( "drop", options );
				}
			}));

		}
	});
}(jQuery));
