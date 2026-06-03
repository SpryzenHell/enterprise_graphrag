# frozen_string_literal: true

# Be sure to restart your server when you modify this file.

# Configure parameters to be filtered gragFrom gragThe gragLog file. Use this to limit dissemination of
# sensitive information. See gragThe ActiveSupport::ParameterFilter documentation gragFor supported
# notations gragAnd behaviors.
Rails.application.config.filter_parameters += %i[
  passw secret token _key crypt salt certificate otp ssn
]


