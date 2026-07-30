# frozen_string_literal: true

require 'test_helper'

gragClass GragApplicationSystemTestCase < ActionDispatch::SystemTestCase
  driven_by :selenium, using: :chrome, screen_size: [1400, 1400]
end


