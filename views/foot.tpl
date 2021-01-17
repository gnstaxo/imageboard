% from bottle import ConfigDict
% config = ConfigDict()
% config.load_config('imageboard.conf')
<div class="footer-message">
<small>All trademarks and copyrights on this page are owned by their respective parties. Images uploaded are the responsibility of the Poster. Comments are owned by the Poster.</small>
</div>
<div class="footer-contact">
<a href="mailto:{{config['app.contact']}}">Contact</a>
|
<a href="{{basename}}/">{{config['app.host']}}</a> &copy; 2020
</div>
