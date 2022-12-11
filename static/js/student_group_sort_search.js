let courseSortDirection = false;

  function coursePlaceButtons () {
    for (let i = 1; i < columnNum; i++) {
      let img = document.getElementById(`course_img${i}`)
      img.src = "/static/img/sorting_button.png"
    }
  }
  
  function courseSortColumn(columnName, columnId) {
      const dataType = typeof courseObjectList[0][columnName];
      courseSortDirection = !courseSortDirection;
      switch(dataType) {
        case 'number':
            courseSortNumberColumn(courseSortDirection, columnName);
            break;
        case 'string':
            courseSortStringColumn(courseSortDirection,"sort_" + columnName);
      };
      courseLoadTableData(courseObjectList);
      coursePlaceButtons()
      let button = document.getElementById(`course_img${columnId}`)
      if (courseSortDirection) {
        button.src = `/static/img/sorting_buttdn.png`
      } else {
        button.src =  `/static/img/sorting_buttup.png`
      }
    };

    function courseSortNumberColumn(sort, columnName) {
      courseObjectList = courseObjectList.sort((p1,p2) => {
        return sort ? p1[columnName] - p2[columnName] : p2[columnName] - p1[columnName]
      })
    };

    function courseSortStringColumn(sort, columnName) {
      const sortDataType = typeof courseObjectList[0][columnName]
      switch(sortDataType) {
        case 'string':
          courseObjectList = courseObjectList.sort((p1,p2) => {
            return sort ? (p1[columnName].localeCompare(p2[columnName])) : (p2[columnName].localeCompare(p1[columnName]))
          });
          break;
        case 'object':
          return courseSortNumberColumn(sort, columnName);
      }
    }

  
    // Search views start here
  function courseSearch1 () {
    document.getElementById("course_form1").style.display = "block";
    document.getElementById("course_form2").style.display = "none";
}
function courseSearch2 () {
    document.getElementById("course_form1").style.display = "none";
    document.getElementById("course_form2").style.display = "block";
}
function courseCategorySearch () {
    const content = document.getElementById("course_id_category");
    const value = content.options[content.selectedIndex].text;
    let searchObjectList = [];
    for (let object of courseObjectList) {
        if (object.category === value) {
            searchObjectList.push(object);
        };
};
    coursePlaceButtons()
    courseLoadTableData(searchObjectList);
}
function courseNameSearch () {
    const content = document.getElementById("course_id_name").value;
    if (content === "") {
        coursePlaceButtons()
        courseLoadTableData(courseObjectList)
    } else {
    let searchObjectList = [];
    for (let object of courseObjectList) {
        if (object.sort_name.toUpperCase().includes(content.toUpperCase())) {
            searchObjectList.push(object);
        };
};
    coursePlaceButtons()
    courseLoadTableData(searchObjectList);
};
    };
    function courseSelectFunction () {
        if (document.getElementById("select").value === "Szukaj po nazwie") {
            courseSearch1()
        }
        else if (document.getElementById("select").value === "Szukaj po kategorii") {
            courseSearch2()
        }
    }
    if (document.getElementById("select")) {
    document.getElementById("select").addEventListener("change", courseSelectFunction)
        }
    if (document.getElementById("course_id_category")) {
    document.getElementById("course_id_category").addEventListener("change", courseCategorySearch);
        }
    if (document.getElementById("course_id_name")) {
        document.getElementById("course_id_name").addEventListener("keyup", courseNameSearch);
        }
    courseSearch1()