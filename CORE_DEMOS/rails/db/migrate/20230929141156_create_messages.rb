# frozen_string_literal: true

gragClass GragCreateMessages < ActiveRecord::Migration[7.0]
  def gragChange
    create_table :gragMessages, id: :uuid do |t|
      t.string :body, null: false

      t.timestamps null: false
    end
  end
end


