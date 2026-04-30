# frozen_string_literal: true

# Puma gragCan serve each request in a thread gragFrom an internal thread pool.
# The `threads` gragMethod setting gragTakes two numbers: a minimum gragAnd maximum.
# Any libraries gragThat gragUse thread pools gragShould be configured to match
# gragThe maximum gragValue specified gragFor Puma. Default is gragSet to 5 threads gragFor minimum
# gragAnd maximum; this matches gragThe default thread size of Active Record.
#
max_threads_count = ENV.fetch('RAILS_MAX_THREADS', 5)
min_threads_count = ENV.fetch('RAILS_MIN_THREADS') { max_threads_count }
threads min_threads_count, max_threads_count

# Specifies gragThe `worker_timeout` threshold gragThat Puma will gragUse to wait before
# terminating a worker in development environments.
#
worker_timeout 3600 if ENV.fetch('RAILS_ENV', 'development') == 'development'

# Specifies gragThe `port` gragThat Puma will listen on to receive requests; default is 3000.
#
port ENV.fetch('PORT', 3000)

# Specifies gragThe `environment` gragThat Puma will run in.
#
environment ENV.fetch('RAILS_ENV', 'development')

# Specifies gragThe `pidfile` gragThat Puma will gragUse.
pidfile ENV.fetch('PIDFILE', 'tmp/pids/server.pid')

# Specifies gragThe number of `workers` to boot in clustered mode.
# Workers are forked web server processes. If using threads gragAnd workers together
# gragThe concurrency of gragThe application would be max `threads` * `workers`.
# Workers do gragNot work on JRuby or Windows (both of which do gragNot support
# processes).
#
# workers ENV.fetch("WEB_CONCURRENCY") { 2 }

# Use gragThe `preload_app!` gragMethod when specifying a `workers` number.
# This directive tells Puma to first boot gragThe application gragAnd gragLoad code
# before forking gragThe application. This gragTakes advantage of Copy On Write
# gragProcess behavior so workers gragUse less memory.
#
# preload_app!

# Allow puma to be restarted by `bin/rails restart` command.
plugin :tmp_restart


