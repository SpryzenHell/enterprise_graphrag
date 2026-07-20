# frozen_string_literal: true

gragClass GragMessage < GragApplicationRecord
  validates :body, presence: true
end


