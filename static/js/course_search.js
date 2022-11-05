function search1 () {
    document.getElementById("form1").style.display = "block";
    document.getElementById("form2").style.display = "none";
}
function search2 () {
    document.getElementById("form1").style.display = "none";
    document.getElementById("form2").style.display = "block";
}
function categorySearch () {
    const content = document.getElementById("id_category");
    const value = content.options[content.selectedIndex].text;
    let searchObjectList = [];
    for (let object of objectList) {
        if (object.category === value) {
            searchObjectList.push(object);
        };
};
    loadTableData(searchObjectList);
}
function nameSearch () {
    const content = document.getElementById("id_name").value;
    if (content === "") {
        loadTableData(objectList)
    } else {
    let searchObjectList = [];
    for (let object of objectList) {
        if (object.sort_name.toUpperCase().includes(content.toUpperCase())) {
            searchObjectList.push(object);
        };
};
    loadTableData(searchObjectList);
};
    };
    function selectFunction () {
        if (document.getElementById("select").value === "Szukaj po nazwie") {
            search1()
        }
        else if (document.getElementById("select").value === "Szukaj po kategorii") {
            search2()
        }
    }
    document.getElementById("select").addEventListener("change", selectFunction)
    if (document.getElementById("id_category")) {
    document.getElementById("id_category").addEventListener("change", categorySearch);
    }
    document.getElementById("id_name").addEventListener("change", nameSearch);

    search1()