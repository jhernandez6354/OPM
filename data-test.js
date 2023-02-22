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
            lRow+=talent[sid][vTalent][i].desc+"<br>";
        }
        lRow+="</div>"
    }
    return lRow
}
const logFileText = async file => {
    const response = await fetch(file)
    const txt = await response.text()
    var value = JSON.parse(txt);
    var data = eval(value);
    var tablearray = [];
    tablearray.push('<div class="table"><div class="table-header"><div class="header__item"><a id="hero" class="filter__link filter__link--number" href="#">Hero</a></div><div class="header__item"><a id="normal" class="filter__link filter__link--number" href="#">Normal Skill</a></div><div class="header__item"><a id="active" class="filter__link filter__link--number" href="#">Active Skill</a></div><div class="header__item"><a id="passive1" class="filter__link filter__link--number" href="#">Passive Skill 1</a></div><div class="header__item"><a id="passive2" class="filter__link filter__link--number" href="#">Passive Skill 2</a></div><div class="header__item"><a id="talent" class="filter__link filter__link--number" href="#">Talent</a></div><div class="header__item"><a id="limit" class="filter__link filter__link--number" href="#">Limiter</a></div></div><div class="table-content">')
    for (id = 0; id < data.length; id++) { //get a count of heroes and assign them to an index.
        hName=data[id].hero;
        tablearray.push('<div class="table-row">')
        var skill = skills(data[id].details.skill);
        var talent = talents(data[id].details.talent);
        var limit = data[id].details.limit
        tablearray.push("<div class=\"table-data\">" + hName+"</div>");
        tablearray.push(skill);
        tablearray.push(talent);
        tablearray.push("<div class=\"table-data\">" + limit+"</div>");
        tablearray.push('</div>')
    }
    tablearray.push("</div></div>");
    document.getElementById("container").innerHTML = tablearray.join('');
}

logFileText('./hero_data/herolist.json')