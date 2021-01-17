<div class="Pagination">
% if current_page != 1:
  % if current_page - 1 == 1:
    <a class="Pagination-arrow" href="{{basename}}/{{board_name}}/"><<</a>
  % else:
    <a class="Pagination-arrow" href="{{basename}}/{{board_name}}/{{current_page - 1}}"><<</a>
  % end
% end
<a class="Pagination-number" href="{{basename}}/{{board_name}}/">1</a>
<%
number = 2
for i in range(per_page, thread_count, per_page):
%>
<a class="Pagination-number" href="{{basename}}/{{board_name}}/{{number}}">{{number}}</a>
<%
number += 1
end
%>
% if number -1 != current_page:
<a class="Pagination-arrow" href="{{basename}}/{{board_name}}/{{current_page + 1}}">>></a>
% end
<a class="Pagination-number Catalog" href="{{basename}}/{{board_name}}/catalog">Catalog</a>
</div>
