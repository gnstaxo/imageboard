% from bottle import ConfigDict
% from json import loads
% config = ConfigDict()
% config.load_config('imageboard.conf')
% report_reasons = loads(config['reports.reasons'])
<div class="Delete-form">
<table>
  <tbody>
    <tr>
      <td>Delete post:</td>
      <td><input type="submit" value="Delete"></td>
    </tr>
    <tr>
    <td>Report post:</td>
      <td>
      <select name="report">
          <option selected disabled>Reason:</option>
        % for reason in report_reasons:
          <option value="{{reason}}">{{reason}}</option>   
        % end
      </select>
      <input type="submit" value="Report">
      </form>
      </td>
    </tr>
  </tbody>
</table>
</div>
<div style="clear:both;"></div>
% include('menu')
% include('foot')
