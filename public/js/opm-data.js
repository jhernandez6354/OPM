var API_URL = 'https://api.thelazygame.com/hero-list';
function skills (skill){
    var lRow="";

    for (sid = 0; sid < skill.length; sid++) {
        for  (sn = 0; sn < skill[sid].length; sn++) {
            var vSkill = Object.keys(skill[sid][sn]);
            lRow+="<dt>"+vSkill+"</dt>"; //the name of the skill
            for (i = 0; i < skill[sid][sn][vSkill].length; i++) {
                lRow+="<dd>"+skill[sid][sn][vSkill][i].desc+"</dd>";
            }
        }
    }
    return lRow
}
function talents (talent){
    var lRow="";
    for (sid = 0; sid < talent.length; sid++) {
        var vTalent = Object.keys(talent[sid]);
        lRow+="<dt>"+vTalent+"</dt>"; //the name of the talent
        for (i = 0; i < talent[sid][vTalent].length; i++) {
            lRow+="<dd>"+talent[sid][vTalent][i].desc+"</dd>";
        }
    }
    return lRow
}

function blessings (bless){
    var lRow="";
    if (Object.keys(bless).length > 0 ){
        lRow="<dt>"+bless['bless_name']+"</dt>"; //the name of the talent
        lRow+="<dd>"+bless['bless_desc']+"</dd>";
    } else {
        lRow="<dt>No Blessing</dt>"
    }
    return lRow
}

function search_hero() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("userin");
    filter = input.value.toUpperCase();
    table = document.getElementsByClassName("table-content")[0];
    tr = table.getElementsByClassName("modal_button");
    
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByClassName("hero_name")[0];
        if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            tr[i].parentElement.parentElement.style.display = "";
        } else {
            tr[i].parentElement.parentElement.style.display = "none";
        }
        }
    }
}

function filter(vfilter,v_class) {
    let data = document.getElementsByClassName(v_class);
    for (let i = 0; i < data.length; i++) {
        if (vfilter.some(v => (data[i].innerHTML).match(v))) {
            data[i].parentElement.closest('details').style = "display:inline-block"
        } else {
            data[i].parentElement.closest('details').style = "display:none"
        }
    }
}


$(document).ready(function(){
    var tablearray = [];
    $.ajax({
        url: API_URL,
        type: 'GET',
        dataType: 'json',
        crossDomain: true,
        success: function(data){
            //tablearray.push('<div class="table"><div class="table-header"><div class="header__item"><a id="normal">Normal Skill</a></div><div class="header__item"><a>Active Skill</a></div><div class="header__item"><a id="passive1" >Passive Skill 1</a></div><div class="header__item"><a id="passive2" >Passive Skill 2</a></div><div class="header__item"><a id="talent" >Talent</a></div><div class="header__item"><a id="limit" >Limiter</a></div><div class="header__item"><a id="blessing" >Blessing</a></div></div>
            tablearray.push('<div class="table-content">')
            vint=0
            for (id = 0; id < data.length; id++) { //get a count of heroes and assign them to an index.
                if (data[id].details.characteristic == '' && data[id].details.type =='Weapon'){
                    v_type="bot-weapon"
                }else{
                    v_type=data[id].details.type
                };
                v_characteristic=(data[id].details.characteristic);
                v_role=(data[id].details.role);
                v_class=(data[id].details.class);
                tablearray.push('<details class=\"hero-details\">')
                tablearray.push("<summary><span class=\"modal_button\" href=\"#myModal"+vint+"\">");
                if (data[id].details.active == false) {
                    tablearray.push("<span class=\"upcoming\" style=\"font-family:Verdana,Geneva,sans-serif\"><strong><span style=\"color:#e74c3c\">\tUPCOMING</span></strong></span>");
                }else {
                    tablearray.push("");
                };
                tablearray.push("<div class=\"hero-attr\" href=\"#myModal"+vint+"\"><img class=\"type_img\" src=\"images\\"+ (v_type).toLowerCase() +".png\" title=\"Type: "+v_type+"\"/>");
                if (v_characteristic != "None") {
                    tablearray.push("<img class=\"type_img\" src=\"images\\"+ v_characteristic.toLowerCase() +".png\" title=\""+v_characteristic+"\"/>");
                };
                if (v_class != "None") {
                    tablearray.push("<img class=\"type_img\" src=\"images\\"+ v_role.toLowerCase() +".png\" title=\""+v_role+"\"/>");
                    tablearray.push("<img class=\"type_img\" src=\"images\\"+ v_class.toLowerCase() +".png\"title=\""+v_class+"\"/>");
                } else{
                    tablearray.push("<img class=\"type_img\" src=\"images\\"+ v_role.toLowerCase() +".png\"title=\""+v_role+"\"/>");
                };
                if(/^\d+$/.test(data[id].shortname) ||data[id].details.active == false) {
                    hero_img=""
                } else {
                    hero_img="<img id=\"hero_icon\" href=\"#myModal"+vint+"\" src=\"images\\avatar_"+ data[id].shortname +"_hero.png\" title=\""+v_role+"\"/>"
                }
                tablearray.push("</div><div class=\"hero_name\" href=\"#myModal"+vint+"\">"+ data[id].hero+"<div class=\"hero_icon\" href=\"#myModal"+vint+"\">"+hero_img+"</div><div id=\"myModal"+vint+"\" class=\"modal\"><div class=\"modal-content\"><div class=\"modal-body\"><dl>")
                var skill = skills(data[id].details.skill);
                var talent = talents(data[id].details.talent);
                var blessing = blessings(data[id].details.blessing);
                var limit = data[id].details.limit
                var mega_limit = data[id].details.mega_limit
                tablearray.push("<h3>Skills</h3>")
                tablearray.push(skill);
                tablearray.push("<h3>Talent</h3>")
                tablearray.push(talent);
                tablearray.push("<h3>Limit Break</h3>")
                tablearray.push("<dd>" + limit+"");
                tablearray.push("</br><b>Mega: </b>" + mega_limit+"</dd>");
                tablearray.push("<h3>Blessing</h3>")
                tablearray.push(blessing);
                tablearray.push('</dl></div></div></div></span></summary></details>')
                v_characteristic,v_role,v_class,v_type=null
                vint++
            }
            tablearray.push("</div");
            document.getElementById("container").innerHTML = tablearray.join('');
        }
    }).done(function() {
        // Get the button that opens the modal
        var btn = document.querySelectorAll("span.modal_button");
        // All page modals
        var modals = document.querySelectorAll('.modal');
        // Get the <span> element that closes the modal
        var spans = document.getElementsByClassName("close");

        // When the user clicks the button, open the modal
        for (var i = 0; i < btn.length; i++) {
            btn[i].onclick = function(e) {
                e.preventDefault();
                modal = document.querySelector(e.target.getAttribute("href"));
                modal.style.display = "block";
        }
        }

        // When the user clicks on <span> (x), close the modal
        for (var i = 0; i < spans.length; i++) {
            spans[i].onclick = function() {
                for (var index in modals) {
                    if (typeof modals[index].style !== 'undefined') modals[index].style.display = "none";    
                }
            }
        }

        // When the user clicks anywhere outside of the modal, close it
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                for (var index in modals) {
                if (typeof modals[index].style !== 'undefined') modals[index].style.display = "none";    
                }
            }
        }
    });

});


//const
const ow_button=document.querySelector('.id_hero_type_0')
const comp_button=document.querySelector('.id_hero_type_1')
const tech_button=document.querySelector('.id_hero_type_2')
const phys_button=document.querySelector('.id_hero_type_3')
const psy_button=document.querySelector('.id_hero_type_4')
const agile_button=document.querySelector('.id_hero_type_5')
const all_button=document.querySelector('.id_hero_all')
//Type Filters
ow_button.addEventListener('click', ()=>filter(["Type: Old World"],"hero-attr"));
comp_button.addEventListener('click', ()=>filter(["Type: Complete"],"hero-attr"));
tech_button.addEventListener('click', ()=>filter(["Type: Tech"],"hero-attr"));
phys_button.addEventListener('click', ()=>filter(["Type: Physical"],"hero-attr"));
psy_button.addEventListener('click', ()=>filter(["Type: Psychic"],"hero-attr"));
agile_button.addEventListener('click', ()=>filter(["Type: Agile"],"hero-attr"));
all_button.addEventListener('click', ()=>filter(["Type: Agile","Type: Old World","Type: Complete","Type: Tech","Type: Physical","Type: Psychic"],"hero-attr"));

document.querySelectorAll('.id_hero_0').forEach(input => input.addEventListener('click', ()=>filter(["Heals the ally","healing self and the ally","Healing to allies"],"modal-content")));
document.querySelectorAll('.id_hero_1').forEach(input => input.addEventListener('click', ()=>filter(["Attack of allies","all allies' Attack"],"modal-content")));
document.querySelectorAll('.id_hero_2').forEach(input => input.addEventListener('click', ()=>filter(["all allies gain a shield"],"modal-content")));
document.querySelectorAll('.id_hero_3').forEach(input => input.addEventListener('click', ()=>filter(["Stun the target", "hance to cause Stun","hance to inflict Stun","and inflicting Stun for"," inflicts Stun on the target","and Stunning them for","causes Stun on all"],"modal-content")));
//Bot Filters
document.querySelectorAll('.id_bot_0').forEach(input => input.addEventListener('click', ()=>filter(["Bots, max level increases by 30 levels","Defender Bots","Attack Bots"],"modal-content")));
