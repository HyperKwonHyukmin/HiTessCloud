// 메뉴 JS
let listElements = document.querySelectorAll('.link');

listElements.forEach(listElement => {
  listElement.addEventListener('click', ()=>{
    if (listElement.classList.contains('active')){
      listElement.classList.remove('active');
    }
    else{
      listElements.forEach (listE => {
        listE.classList.remove('active');
      })
      listElement.classList.toggle('active');
    }
  })
})

// Loading page
const analysis_btn = document.querySelector('.calculate_btn_nas_support');
const loading_class = document.querySelector('.loading');
analysis_btn.addEventListener('click', Loading_page_view);

function Loading_page_view() {
  loading_class.style.display = 'block';
}
















