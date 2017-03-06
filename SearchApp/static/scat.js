function showWordDetails(url) {
	window.open(url, "wordDetails", "menubar=no,status=no,toolbar=no,height=300,width=300,scrollbars=yes", false);	
}

function hghltWord(gd) {
		var word = document.getElementById(gd.getAttribute("for"));
		word.className = word.className + " hastooltiphover";
}

function dehghltWord(gd) {
		var word = document.getElementById(gd.getAttribute("for"));
		word.className = word.className.replace(" hastooltiphover","");
}

function hghltGD(word) {
		var gd = document.getElementById("gd." + word.id);
		gddiv = document.getElementById("showGramData");
		gd.className = "highlighted";
		if ((gd.offsetTop > gddiv.offsetHeight + gddiv.scrollTop) || 
			(gd.offsetTop < gddiv.scrollTop)) {
			gddiv.scrollTop = gd.offsetTop;	
		}
}

function dehghltGD(word) {
		var gd = document.getElementById("gd." + word.id);
		gd.className = "";
}

function addFilterField(select) {
		filterID = select.value;
		if (filterID != null)
		{
			document.getElementById(filterID).style.display = "block";
			select.removeChild(document.getElementById(filterID + "_selectoption"));
		}		
}
