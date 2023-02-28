//To Test, run the following command in your terminal:
    // python -m http.server
// Open up your browser to http://127.0.0.1:8000/test.html


function skills (skill){
    var lRow="";

    for (sid = 0; sid < skill.length; sid++) {
        for  (sn = 0; sn < skill[sid].length; sn++) {
            var vSkill = Object.keys(skill[sid][sn]);
            lRow+="<div class=\"table-data\"><div class=\"title\">"+vSkill+"</div>"; //the name of the skill
            for (i = 0; i < skill[sid][sn][vSkill].length; i++) {
                lRow+="<li>"+skill[sid][sn][vSkill][i].desc+"</li><br>";
            }
            lRow+="</div>"
        }
    }
    return lRow
}
  
function talents (talent){
    var lRow="";
    for (sid = 0; sid < talent.length; sid++) {
        var vTalent = Object.keys(talent[sid]);
        lRow+="<div class=\"table-data\"><div class=\"title\">"+vTalent+"</div>"; //the name of the talent
        for (i = 0; i < talent[sid][vTalent].length; i++) {
            lRow+="<li>"+talent[sid][vTalent][i].desc+"</li><br>";
        }
        lRow+="</div>"
    }
    return lRow
}

function blessings (bless){
    var lRow="";
    if (Object.keys(bless).length > 0 ){
        lRow="<div class=\"table-data\"><div class=\"title\">"+bless['bless_name']+"</div>"; //the name of the talent
        lRow+=bless['bless_desc']+"<br></div>";
    } else {
        lRow="<div class=\"table-data\">No Blessing<br></div>"
    }
    return lRow
}

function search_hero() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("userin");
    filter = input.value.toUpperCase();
    table = document.getElementsByClassName("table-content")[0];
    tr = table.getElementsByClassName("hero-details");
    
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByClassName("hero")[0];
        if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
        }
    }
}

function filter(event, filter) {
    let element = event.target;
    let data = document.getElementsByClassName("table-data");
    for (let i = 0; i < data.length; i++) {
        if (filter.some(v => (data[i].innerHTML).includes(v))) {
            if (element.checked == true) {
                data[i].parentElement.closest('details').style = "display:inline-block"
            } else {
                data[i].parentElement.closest('details').style = "display:none"
            }
        }
    }
}

function filter_bots(event) {
    let element = event.target;
    let data = document.getElementsByClassName("hero");
    let bots=["Laser","Spike","Potion","Waste Oil","Electric Current","Operator","Iron Falcon","Cannon","Electric Saw","Door Board","Earthquake","Iron Hammer"];
    for (let i = 0; i < data.length; i++) {
        if (bots.some(v => (data[i].innerHTML).includes(v))) {
            if (element.checked == true) {
                data[i].parentElement.closest('details').style = "display:inline-block"
            } else {
                data[i].parentElement.closest('details').style = "display:none"
            }
        }
    }
}

const logFileText = async file => {
    const response = await fetch(file)
    const txt = await response.text()
    var value = JSON.parse(txt);
    var data = eval(value);
    var tablearray = [];
    tablearray.push('<div class="table"><div class="table-header"><div class="header__item"><a id="normal">Normal Skill</a></div><div class="header__item"><a>Active Skill</a></div><div class="header__item"><a id="passive1" >Passive Skill 1</a></div><div class="header__item"><a id="passive2" >Passive Skill 2</a></div><div class="header__item"><a id="talent" >Talent</a></div><div class="header__item"><a id="limit" >Limiter</a></div><div class="header__item"><a id="blessing" >Blessing</a></div></div><div class="table-content">')
    for (id = 0; id < data.length; id++) { //get a count of heroes and assign them to an index.
        hName=data[id].hero;
        tablearray.push('<details class="hero-details">')
        tablearray.push("<summary><span class=\"hero\">"+ hName+"</span></summary>");
        tablearray.push('<div class="table-row">')
        var skill = skills(data[id].details.skill);
        var talent = talents(data[id].details.talent);
        var blessing = blessings(data[id].details.blessing);
        var limit = data[id].details.limit
        tablearray.push(skill);
        tablearray.push(talent);
        tablearray.push("<div class=\"table-data\">" + limit+"</div>");
        tablearray.push(blessing);
        tablearray.push('</div></details>')
    }
    tablearray.push("</div></div>");
    document.getElementById("container").innerHTML = tablearray.join('');
}

logFileText('./hero_data/herolist.json')
//Hero Filters
document.querySelectorAll('.id_hero_0').forEach(input => input.addEventListener('input', ()=>filter(event,["Heals the ally","healing self and the ally","Healing to allies"])));
document.querySelectorAll('.id_hero_1').forEach(input => input.addEventListener('input', ()=>filter(event,["Attack of allies","all allies' Attack"])));
document.querySelectorAll('.id_hero_2').forEach(input => input.addEventListener('input', ()=>filter(event,["all allies gain a shield"])));
document.querySelectorAll('.id_hero_3').forEach(input => input.addEventListener('input', ()=>filter(event,["Stun the target", "hance to cause Stun","hance to inflict Stun","and inflicting Stun for"," inflicts Stun on the target","and Stunning them for","causes Stun on all"])));
//Bot Filters
document.querySelectorAll('.id_bot_0').forEach(input => input.addEventListener('input', ()=>filter(event,["Bots, max level increases by 30 levels","Defender Bots","Attack Bots"])));
document.querySelector('.id_bot_1').addEventListener('input', ()=>filter_bots(event));
