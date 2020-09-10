function compute() {
	var wizards = parseInt(document.querySelector('#wizards').value);
	var clerics = parseInt(document.querySelector('#clerics').value);
	var rogues = parseInt(document.querySelector('#rogues').value);
	var warriors = parseInt(document.querySelector('#warriors').value);
	var wildcards = parseInt(document.querySelector('#wildcards').value);
	var draws = parseInt(document.querySelector('#draws').value);
	var trials = parseInt(document.querySelector('#trials').value);

	var party_sizes = [0,0,0,0,0];

	for (var i = 0; i<trials; i++) {
		// Generate 7 + draws distinct random numbers from 0 to 39

		var hand = new Set();
		for (var card = 0; card<7+draws; card++) {
			var n = Math.floor(Math.random()*40);
			while (hand.has(n)) {
				n = Math.floor(Math.random()*40);
			}
			hand.add(n);
		}
		var party_size = 0;
		var at = 0;
		for (w=at; w<at+wizards; w++) {
			if (hand.has(w)) {
				party_size += 1;
				break;
			}
		}
		at += wizards;
		for (w=at; w<at+clerics; w++) {
			if (hand.has(w)) {
				party_size += 1;
				break;
			}
		}
		at += clerics;
		for (w=at; w<at+warriors; w++) {
			if (hand.has(w)) {
				party_size += 1;
				break;
			}
		}
		at += warriors;
		for (w=at; w<at+rogues; w++) {
			if (hand.has(w)) {
				party_size += 1;
				break;
			}
		}
		at += rogues;
		for (w=at; w<at+wildcards; w++) {
			if (party_size==4) {
				break;
			}
			if (hand.has(w)) {
				party_size += 1;
			}
		}
		at += wildcards;
		party_sizes[party_size]+=1;
	}

	document.querySelector('#size0').textContent = Math.round(1000*party_sizes[0]/trials)/10+"%";
	document.querySelector('#size1').textContent = Math.round(1000*party_sizes[1]/trials)/10+"%";
	document.querySelector('#size2').textContent = Math.round(1000*party_sizes[2]/trials)/10+"%";
	document.querySelector('#size3').textContent = Math.round(1000*party_sizes[3]/trials)/10+"%";
	document.querySelector('#size4').textContent = Math.round(1000*party_sizes[4]/trials)/10+"%";
	document.querySelector('#EV').textContent = Math.round(100*(party_sizes[1] + 2*party_sizes[2] + 3*party_sizes[3] + 4*party_sizes[4])/trials)/100;
}
