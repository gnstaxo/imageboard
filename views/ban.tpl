% rebase('base', title="Ban info")

% if current_user.banned:
  <div class="Ban">
    This IP is banned.<br><b>Reason:</b>{{current_user.ban_reason}}<br><b>Date:</b>{{current_user.ban_date}}
  </div>
% else:
  <div class="Ban">
    This IP is not banned.
  </div>
% end
