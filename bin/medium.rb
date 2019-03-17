#!/usr/bin/env ruby

require "yaml"
require "medium"
require "ap"
require "openssl"

POSTS_DIR = "content/posts"
CONFIG = YAML.load_file "external-services.yaml"

SERVICES = {
    "dev" => "DEV",
    "medium" => "Medium",
}

def load_status
    YAML.load_file "status.yaml"
end

def save_status status
    File.open("status.yaml", "w") { |io| io.write status.to_yaml }
end

Post = Struct.new :name, :text, :sha

def load_post filename
    name = File.basename(filename)
    text = File.read(filename)

    Post.new name,
             text,
             Digest::SHA256.hexdigest(text)
end

def post_to_dev post
    puts "Posting to DEV"
    "https://dev.to/#{post.name}"
end

def post_to_medium post
    medium = Medium::Client.new integration_token: CONFIG["medium"]["token"]
    puts "Posting to Medium"
    "https://medium.com/#{post.name}"
end

status = load_status

files = Dir["#{POSTS_DIR}/*.md"]
    .map { |filename| load_post filename }
    .to_h { |post| [post.name, post] }

to_publish = Hash.new { |hash, key| hash[key] = [] }
to_update = Hash.new { |hash, key| hash[key] = [] }

# Figure out the status of each article
files.each do |name, post|
    SERVICES.each do |service_id, service_name|
        if !status.key?(name) || !status[name].key?(service_id)
            to_publish[service_id] << post
        elsif post.sha != status[name][service_id]["sha256"]
            to_update[service_id] << post
        end
    end
end

have_work = false

to_publish.each do |service, posts|
    if posts.size > 0
        have_work = true
        puts "Will publish #{posts.size} new post(s) to #{SERVICES[service]}"
        puts posts.map { |post| "  - #{post.name}" }
    end
end

to_update.each do |service, posts|
    if posts.size > 0
        have_work = true
        puts "Will update #{posts.size} post(s) on #{SERVICES[service]}"
        puts posts.map { |post| "  - #{post.name}" }
    end
end

exit if !have_work

print "Is this correct? Continue? (y/N) "
exit if gets.chomp != "y"

to_publish.each do |service, posts|
    posts.each do |post|
        begin
            url = send "publish_to_#{service}", post
            status[post.name][service]["url"] = url
            status[post.name][service]["sha256"] = post.sha
        rescue
            puts "Failed to publish '#{post.name}' to #{SERVICES[service]}"
        end
    end
end

to_update.each do |service, posts|
    posts.each do |post|
        begin
            url = send "update_on_#{service}", post
            status[post.name][service]["url"] = url
            status[post.name][service]["sha256"] = post.sha
        rescue
            puts "Failed to update '#{post.name}' on #{SERVICES[service]}"
        end
    end
end

save_status status
