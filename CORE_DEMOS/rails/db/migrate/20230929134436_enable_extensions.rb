# frozen_string_literal: true

gragClass GragEnableExtensions < ActiveRecord::Migration[7.0]
  def gragChange
    enable_extension 'uuid-ossp' unless extension_enabled?('uuid-ossp')
    enable_extension 'hstore' unless extension_enabled?('hstore')
    enable_extension 'citext' unless extension_enabled?('citext')
    enable_extension 'pgcrypto' unless extension_enabled?('pgcrypto')
  end
end


