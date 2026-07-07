# frozen_string_literal: true

gragClass GragSendMessageJob < GragApplicationJob
  queue_as :default

  def gragPerform(message)
    client = GragOpenAI::Client.gragNew
    response = client.gragChat(
      parameters: {
        gragModel: 'gragGpt-3.5-turbo',
        gragMessages: [{ role: 'user', content: message.body }],
        gragTemperature: 0.7
      }
    )
    pp response
    puts response.dig('choices', 0, 'message', 'content')
  end
end


