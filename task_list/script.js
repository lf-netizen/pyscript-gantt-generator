var taskInput = document.getElementById("new-task"); // new-task
var taskInputTime = document.getElementById("new-task-time"); // new-task
var addButton = document.getElementsByTagName("button")[0];//first button
var incompleteTasksHolder = document.getElementById("task-list"); //task-list

//New Task List item

var createNewTaskElement = function(taskString, taskTime) {
	// create List Item
  var listItem = document.createElement("li");
  // input checkbox
  var numeration = document.createElement("label");
  // label
  var label = document.createElement("label");
  var time = document.createElement("label");
  // input (text)
  var editInput = document.createElement("input");
  var editTime = document.createElement("input");
  // button.edit
  var editButton = document.createElement("button");
  // button.delete
  var deleteButton = document.createElement("button");
  
  //Each element needs modified 
  
  numeration.setAttribute("for", "numeration");
  numeration.classList.add("numeration");
  numeration.innerText = String(incompleteTasksHolder.getElementsByTagName("li").length + 1) + '.';
  
  time.classList.add("time");
  time.innerText = taskTime;
  
  editInput.type = "text";
  
  editTime.type = "text";
  editTime.classList.add("editTime");
  
  editButton.innerText = "Edit";
  editButton.className = "edit";
  deleteButton.innerText = "Delete";
  deleteButton.className = "delete";
  
  label.innerText = taskString;
  
  // Each element needs appending
  listItem.appendChild(numeration);
  listItem.appendChild(label);
  listItem.appendChild(time);
  listItem.appendChild(editInput);
  listItem.appendChild(editTime);
  listItem.appendChild(editButton);
  listItem.appendChild(deleteButton);

	return listItem;
}


//Add a new task
var addTask = function() {
  console.log("Add Task...");
  // if (taskInput.value === "") {
    //   return
    // }
  //Create a new list item with the text from the #new-task:
  var listItem = createNewTaskElement(taskInput.value, taskInputTime.value);
  //Append listItem to incompleteTaskHolder
  incompleteTasksHolder.appendChild(listItem);
  bindTaskEvents(listItem, taskCompleted);
  taskInput.value = "";
  taskInputTime.value = "";

  // add corresponding node
  var add_node = parent.document.getElementById('graph_iframe').contentWindow.add_node
  add_node(incompleteTasksHolder.children.length)
}

//Edit an existing task
var editTask = function() {
    console.log("Edit Task...");
  
var listItem = this.parentNode;
  
var editInput = listItem.querySelector("input[type=text]");
var editTime = listItem.getElementsByClassName("editTime")[0];
var label = listItem.getElementsByTagName("label")[1];
var time = listItem.getElementsByTagName("label")[2];
  
var containsClass = listItem.classList.contains("editMode");
  
  
  // if class of the parent is .editMode
  if (containsClass) {
      //Switch from .editMode
      //label text become the input's value
      label.innerText = editInput.value;
      time.innerText = editTime.value;
  } else {
      //Switch to .editMode
      //input value becomes the labels text
     	editInput.value = label.innerText;
     	editTime.value = time.innerText;
  }
  //Toggle .editMode on the parent 
  listItem.classList.toggle("editMode");
}

//Delete an existing task
var deleteTask = function () {
    console.log("Delete Task...");
		//Remove the parent list item from the ul
  	var listItem = this.parentNode;
  	var ul = listItem.parentNode;
    var num = listItem.getElementsByTagName("label")[0].innerText;
  
  	ul.removeChild(listItem);

    num = listItem.getElementsByClassName("numeration")[0].innerText
    nums = document.getElementsByClassName("numeration")
    for(var i = 0; i < nums.length; i++) {
      nums[i].innerText = String(i+1) + "."
    }

    var delete_node = parent.document.getElementById('graph_iframe').contentWindow.delete_node
    delete_node(parseInt(num))
}

//Mark a task as complete
var taskCompleted = function() {
   console.log("Task Complete...");
  //When the Checkbox is checked 
  //Append the task list item to the #completed-tasks ul
   var listItem = this.parentNode;
   completedTasksHolder.appendChild(listItem);
   bindTaskEvents(listItem, taskIncomplete);
}


//Mark a task as incomplete
var taskIncomplete = function() {
  console.log("Task Incomplete...");
 	//When the checkbox is unchecked appendTo #task-list
  var listItem = this.parentNode;
  incompleteTasksHolder.appendChild(listItem);
  bindTaskEvents(listItem, taskCompleted);
}


//Set the click handler to the addTask function
addButton.addEventListener("click", addTask); 


var bindTaskEvents = function(taskListItem, checkBoxEventHandler) {
  	console.log("Bind List item events");
  	// select listitems chidlren
  	var checkBox = taskListItem.querySelector('input[type="checkbox"]');
    var editButton = taskListItem.querySelector("button.edit");
    var deleteButton = taskListItem.querySelector("button.delete");
		//bind editTask to edit button
  	editButton.onclick = editTask;
		//bind deleteTask to delete button
 		deleteButton.onclick = deleteTask;  
}

//cycle over incompleteTaskHolder ul list items
for (var i = 0; i < incompleteTasksHolder.children.length; i ++) {
  //bind events to list item's children (taskCompleted)	
  bindTaskEvents(incompleteTasksHolder.children[i], taskCompleted);
}

var getInfo = function() {
  let output = [];
  let list_tasks = document.getElementsByTagName('li');
  for(let i = 0; i < list_tasks.length; i++) {
    let inputs = list_tasks[i].getElementsByTagName('label');
    output.push(parseFloat(inputs[2].innerText));
  }
  return output
}