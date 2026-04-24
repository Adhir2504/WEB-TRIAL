function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function getCSRFToken() {
  return getCookie('csrftoken');
}

function showStatus(message, type = 'info') {
  const status = $('#api-status');
  status.text(message).removeClass('alert-info alert-success alert-error');
  status.addClass(type === 'success' ? 'alert-success' : type === 'error' ? 'alert-error' : 'alert-info');
  status.show();
}

function clearStatus() {
  $('#api-status').hide();
}

function renderFacilities(data) {
  const tbody = $('#facilities-table tbody');
  tbody.empty();

  if (!data || data.length === 0) {
    tbody.append('<tr><td colspan="5">No facilities found.</td></tr>');
    return;
  }

  data.forEach(function(item) {
    const row = $('<tr>');
    row.append($('<td>').text(item.facility_name));
    row.append($('<td>').text(item.facility_type));
    row.append($('<td>').text(item.location));
    row.append($('<td>').text(item.facility_status));

    const actions = $('<td>');
    const editButton = $('<button>')
      .addClass('btn btn-secondary')
      .text('Edit')
      .on('click', function() {
        openEdit(item.facility_id, item.facility_name, item.facility_type, item.location, item.description, item.facility_status);
      });

    const deleteButton = $('<button>')
      .addClass('btn btn-danger')
      .text('Delete')
      .on('click', function() {
        deleteFacility(item.facility_id);
      });

    actions.append(editButton, ' ', deleteButton);
    row.append(actions);
    tbody.append(row);
  });
}

function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function loadFacilities() {
  clearStatus();
  $.get('/api/facilities/')
    .done(function(data) {
      renderFacilities(data);
      showStatus('Facilities loaded successfully.', 'success');
    })
    .fail(function(xhr) {
      showStatus('Unable to load facilities: ' + xhr.statusText, 'error');
    });
}

function createFacility(event) {
  event.preventDefault();
  clearStatus();

  const payload = {
    facility_name: $('#facility-name').val().trim(),
    facility_type: $('#facility-type').val(),
    location: $('#facility-location').val().trim(),
    description: $('#facility-description').val().trim(),
    facility_status: $('#facility-status').val(),
  };

  $.ajax({
    url: '/api/facilities/',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(payload),
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  })
    .done(function() {
      $('#facility-create-form')[0].reset();
      loadFacilities();
      showStatus('Facility created successfully.', 'success');
    })
    .fail(function(xhr) {
      const error = xhr.responseJSON ? JSON.stringify(xhr.responseJSON) : xhr.statusText;
      showStatus('Create failed: ' + error, 'error');
    });
}

function openEdit(id, name, type, location, description, status) {
  $('#facility-id').val(id);
  $('#edit-facility-name').val(name);
  $('#edit-facility-type').val(type);
  $('#edit-facility-location').val(location);
  $('#edit-facility-description').val(description);
  $('#edit-facility-status').val(status);
  $('#update-section').show();
  $('html, body').animate({ scrollTop: $('#update-section').offset().top }, 300);
}

function updateFacility(event) {
  event.preventDefault();
  clearStatus();

  const facilityId = $('#facility-id').val();
  const payload = {
    facility_name: $('#edit-facility-name').val().trim(),
    facility_type: $('#edit-facility-type').val(),
    location: $('#edit-facility-location').val().trim(),
    description: $('#edit-facility-description').val().trim(),
    facility_status: $('#edit-facility-status').val(),
  };

  $.ajax({
    url: '/api/facilities/' + facilityId + '/',
    method: 'PATCH',
    contentType: 'application/json',
    data: JSON.stringify(payload),
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  })
    .done(function() {
      $('#facility-update-form')[0].reset();
      $('#update-section').hide();
      loadFacilities();
      showStatus('Facility updated successfully.', 'success');
    })
    .fail(function(xhr) {
      const error = xhr.responseJSON ? JSON.stringify(xhr.responseJSON) : xhr.statusText;
      showStatus('Update failed: ' + error, 'error');
    });
}

function deleteFacility(id) {
  clearStatus();
  if (!confirm('Delete this facility?')) {
    return;
  }

  $.ajax({
    url: '/api/facilities/' + id + '/',
    method: 'DELETE',
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  })
    .done(function() {
      loadFacilities();
      showStatus('Facility deleted successfully.', 'success');
    })
    .fail(function(xhr) {
      const error = xhr.responseJSON ? JSON.stringify(xhr.responseJSON) : xhr.statusText;
      showStatus('Delete failed: ' + error, 'error');
    });
}

$(document).ready(function() {
  $('#facility-create-form').on('submit', createFacility);
  $('#facility-update-form').on('submit', updateFacility);
  $('#cancel-edit').on('click', function() {
    $('#facility-update-form')[0].reset();
    $('#update-section').hide();
    clearStatus();
  });
  $('#refresh-table').on('click', function() {
    loadFacilities();
  });
  loadFacilities();
});
