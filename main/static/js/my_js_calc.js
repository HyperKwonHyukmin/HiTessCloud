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

// // modal 띄우는 함수 
// let modal = document.getElementById('modal_notice');

// function openModal() {
//   modal.classList.add('active')
//   //$('.modal').addClass('active')
// }
// function closeModal() {
//   modal.classList.remove('active')
//   // $('.modal').removeClass('active')
// }


//  Post_Mast 응력 계산을 하는 함수 
document.querySelector('.calculate_btn_calc_post').addEventListener('click', postmast_calculation);

function postmast_calculation (e) {  
  e.preventDefault();
  const Post_Height = parseFloat(document.getElementById('Post_Height').value);
  const Higher_Platform_Weight = parseFloat(document.getElementById('Higher_Platform_Weight').value);
  const Higher_Platform_Height = parseFloat(document.getElementById('Higher_Platform_Height').value);
  const Lower_Platform_Weight = parseFloat(document.getElementById('Lower_Platform_Weight').value);
  const Lower_Platform_Height = parseFloat(document.getElementById('Lower_Platform_Height').value);
  const Outer_diameter = parseFloat(document.getElementById('Outer_diameter').value);
  const Thickness = parseFloat(document.getElementById('Thickness').value);
  const Yield_stress = parseFloat(document.getElementById('Yield_stress').value);
  const X_acc = parseFloat(document.getElementById('X_acc').value);
  const Y_acc = parseFloat(document.getElementById('Y_acc').value);
  const Z_acc = parseFloat(document.getElementById('Z_acc').value);    

  Area = (Math.PI * (Math.pow(Outer_diameter,2) - Math.pow((Outer_diameter-2*Thickness),2)))/4
  Moment_of_Inertia = (Math.PI * (Math.pow(Outer_diameter,4) - Math.pow((Outer_diameter-2*Thickness),4)))/64
  Section_Modulus = (Math.PI * (Math.pow(Outer_diameter,4) - Math.pow((Outer_diameter-2*Thickness),4)))/(32*Outer_diameter)

  Post_Weight = Post_Height * Area * 0.00000785
  Bracket_Height = 0

  // Bracket_D를 구하는 방법
  transformed_Post_Height = String(parseInt(Post_Height*0.2));
  temp = transformed_Post_Height.slice(-2); //문자열로 바꾸어 100이하인 뒤에 두자리만 가지고 온다. 
  transformed_Post_Height = parseFloat(temp);

  if (0 <= transformed_Post_Height & transformed_Post_Height < 35) {
    Bracket_Height = (Math.floor(Post_Height*0.2/100)) * 100 //소수점을 버리고 정수만 가지고 와서 계산
  }
  else if (35 <= transformed_Post_Height & transformed_Post_Height < 70){
    Bracket_Height = (Math.floor(Post_Height*0.2/100)) * 100 + 50
  }
  else if (70 <= transformed_Post_Height & transformed_Post_Height < 99){
    Bracket_Height = (Math.floor(Post_Height*0.2/100)) * 100 + 100
  }

  Total_Weight = Post_Weight + Higher_Platform_Weight + Lower_Platform_Weight;
  Loading_Height = (Post_Weight * Post_Height * 0.5 + Higher_Platform_Weight * Higher_Platform_Height + Lower_Platform_Weight * Lower_Platform_Height)/Total_Weight - Bracket_Height * 2/3;

  Fh = Total_Weight * 9.8 * Math.sqrt(Math.pow(X_acc,2) + Math.pow(Y_acc,2));
  Fz = Total_Weight * 9.8 * (1+Z_acc);

  Maximum_Bending_Stress = (Fz / Area) + (Fh * Loading_Height / Section_Modulus);
  Maximum_Shear_Stress = Fh / Area;

  Maximum_Equivalent_Stress = Math.sqrt(Maximum_Bending_Stress**2 + Maximum_Shear_Stress**2);
  Maximum_Displacement = (Fh * Loading_Height**2) * (3*Post_Height-Loading_Height) / (6*206000*Moment_of_Inertia);
  Allowable_Equivalent_Stress = Yield_stress*0.8;
  Allowable_Displacement = Post_Height / 500;

  let Stress_Assessment = (Maximum_Equivalent_Stress < Allowable_Equivalent_Stress)? 'OK' : 'Not OK';
  let Displacement_Assessment = (Maximum_Displacement < Allowable_Displacement)? 'OK' : 'Not OK';

  document.getElementById('Post_Weight').setAttribute('value', String(Post_Weight.toFixed(1)));
  document.getElementById('Bracket_Height').setAttribute('value', String(Bracket_Height.toFixed(1)));
  document.getElementById('Total_Weight').setAttribute('value', String(Total_Weight.toFixed(1)));
  document.getElementById('Loading_Height').setAttribute('value', String(Loading_Height.toFixed(1)));
  document.getElementById('Fh').setAttribute('value', String(Fh.toFixed(1)));
  document.getElementById('Fz').setAttribute('value', String(Fz.toFixed(1)));
  document.getElementById('Area').setAttribute('value', String(Area.toFixed(1)));
  document.getElementById('Moment_of_Inertia').setAttribute('value', String(Moment_of_Inertia.toFixed(1)));
  document.getElementById('Section_Modulus').setAttribute('value', String(Section_Modulus.toFixed(1)));
  document.getElementById('Maximum_Bending_Stress').setAttribute('value', String(Maximum_Bending_Stress.toFixed(1)));
  document.getElementById('Maximum_Shear_Stress').setAttribute('value', String(Maximum_Shear_Stress.toFixed(1)));
  document.getElementById('Maximum_Equivalent_Stress').setAttribute('value', String(Maximum_Equivalent_Stress.toFixed(1)));
  document.getElementById('Maximum_Displacement').setAttribute('value', String(Maximum_Displacement.toFixed(1)));
  document.getElementById('Allowable_Equivalent_Stress').setAttribute('value', String(Allowable_Equivalent_Stress.toFixed(1)));
  document.getElementById('Allowable_Displacement').setAttribute('value', String(Allowable_Displacement.toFixed(1)));
  document.getElementById('Stress_Assessment').setAttribute('value', Stress_Assessment);
  document.getElementById('Displacement_Assessment').setAttribute('value', Displacement_Assessment);

  document.getElementById('Maximum_Bending_Stress').style.color = 'black';
  document.getElementById('Maximum_Shear_Stress').style.color = 'black';
  document.getElementById('Maximum_Equivalent_Stress').style.color = 'black';
  document.getElementById('Maximum_Displacement').style.color = 'black';
  document.getElementById('Allowable_Equivalent_Stress').style.color = 'black';
  document.getElementById('Allowable_Displacement').style.color = 'black';
  document.getElementById('Stress_Assessment').style.color = 'red';
  document.getElementById('Displacement_Assessment').style.color = 'red';

  alert('구조 검토 완료');
}














