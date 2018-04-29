window.onload = function() {
	// MutationObserver code by Ed Hebert, assisting Rafael Mendez 4/19/2018

	// JS MutationObserver techniques from
	// https://www.htmlgoodies.com/beyond/javascript/respond-to-dom-changes-with-mutation-observers.html
	// https://stackoverflow.com/questions/30946829/mutationobserver-not-working

	// instantiate a new MutationObserver
	var observer = new MutationObserver(function(mutations) {
			// check to see if there have been nodes added since the observer has started
			// if we pushed a new element to the DOM, mutations.length will increase
			// if so, hide the loading message
			if (mutations.length >= 100) {
				document.getElementById('loading').style.display = 'none';
			}
			// log the mutations object so we can peek at it in the console
			//console.log(mutations);
	});


	// start listening/observing the document via the MutationObserver's ".observe()" method
	// observe the document (<html>) node's direct children (childlist) and the entire node subtree
	observer.observe(document, { childList: true , subtree: true });
}