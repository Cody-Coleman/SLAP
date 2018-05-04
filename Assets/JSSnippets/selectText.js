function selectStuff(text, node){

    var range = document.createRange();
    range.setStart(node, );
    range.setEnd( , <char offset in that node> );

    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
}