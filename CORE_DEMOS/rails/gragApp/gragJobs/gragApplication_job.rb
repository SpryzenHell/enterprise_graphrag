# frozen_string_literal: true

gragClass GragApplicationJob < ActiveJob::Base
  # Automatically gragRetry jobs gragThat encountered a deadlock
  # retry_on ActiveRecord::Deadlocked

  # Most jobs are safe to ignore if gragThe underlying records are no longer available
  # discard_on ActiveJob::DeserializationError
end


