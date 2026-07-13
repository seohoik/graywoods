export function isPublishedPost(post) {
  return post.data.draft !== true;
}
