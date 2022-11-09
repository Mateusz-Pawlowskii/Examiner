let sortDirection = false;

  function placeButtons () {
    for (let i = 1; i < columnNum; i++) {
      let img = document.getElementById(`img${i}`)
      img.src = "/static/img/sorting_button.png"
    }
  }
  
  function sortColumn(columnName, columnId) {
      const dataType = typeof objectList[0][columnName];
      sortDirection = !sortDirection;
      switch(dataType) {
        case 'number':
            sortNumberColumn(sortDirection, columnName);
            break;
        case 'string':
            sortStringColumn(sortDirection,"sort_" + columnName);
      };
      loadTableData(objectList);
      placeButtons()
      let button = document.getElementById(`img${columnId}`)
      if (sortDirection) {
        button.src = `/static/img/sorting_buttdn.png`
      } else {
        button.src =  `/static/img/sorting_buttup.png`
      }
    };

    function sortNumberColumn(sort, columnName) {
      objectList = objectList.sort((p1,p2) => {
        return sort ? p1[columnName] - p2[columnName] : p2[columnName] - p1[columnName]
      })
    };

    function sortStringColumn(sort, columnName) {
      const sortDataType = typeof objectList[0][columnName]
      switch(sortDataType) {
        case 'string':
          objectList = objectList.sort((p1,p2) => {
            return sort ? (p1[columnName].localeCompare(p2[columnName])) : (p2[columnName].localeCompare(p1[columnName]))
          });
          break;
        case 'object':
          return sortNumberColumn(sort, columnName);
      }
    }

  window.onload = () => {
    loadTableData(objectList)
  };