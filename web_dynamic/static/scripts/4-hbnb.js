$(document).ready(function () {
  let checkedAmenities = [];
  const checkedAmenitiesIds = [];

  /* Show API status */

  $.getJSON('http://0.0.0.0:5001/api/v1/status/', function (data) {
    if (data.status === 'OK') {
      $('#api_status').addClass('available');
    } else {
      $('#api_status').removeClass('available');
    }
  });

  $('#btn_search').on('click', function () {
    $.ajax('http://0.0.0.0:5001/api/v1/places_search', {
      data: JSON.stringify({
        amenities: checkedAmenitiesIds
      }),
      contentType: 'application/json',
      type: 'POST',
      success: function (data) {
        for (const place of data) {
          const template = `<article>
            <div class="title_box">
              <h2>${place.name}</h2>
              <div class="price_by_night">$${place.price_by_night}</div>
            </div>
            <div class="information">
              <div class="max_guest">${place.max_guest} Guests</div>
                    <div class="number_rooms">${place.number_rooms} Bedrooms</div>
                    <div class="number_bathrooms">${place.number_bathrooms} Bathrooms</div>
            </div>
            <div class="description">
              ${place.description}
            </div>
          </article>`;
          $('section.places').append(template);
        }
      }
    });
  });

  /* Make amenities filter dynamic */

  function fillHeader () {
    checkedAmenities = checkedAmenities.filter((item) => item !== '');
    if (checkedAmenities.length > 1) {
      let stringAmenities = checkedAmenities.join(', ');

      if (stringAmenities.length > 38) {
        stringAmenities = stringAmenities.slice(0, 37) + '...';
      }

      $('.checkedAmenities').text(stringAmenities);
    } else if (checkedAmenities.length === 1) {
      $('.checkedAmenities').text(checkedAmenities[0]);
    } else {
      $('.checkedAmenities').text('');
    }
  }

  $('.amenity-checkbox').on('change', function () {
    const amenityName = $(this).attr('data-name');
    const amenityId = $(this).attr('data-id');

    if ($(this).prop('checked')) {
      checkedAmenitiesIds.push(amenityId);
      checkedAmenities.push(amenityName);
      fillHeader();
    } else {
      checkedAmenitiesIds.splice(checkedAmenitiesIds.indexOf(amenityId), 1);
      checkedAmenities.splice(checkedAmenities.indexOf(amenityName), 1);
      fillHeader();
    }
  });
});
